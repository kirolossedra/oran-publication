/*
 * Software Name: ib-ORAN
 * SPDX-FileCopyrightText: Copyright (c) Orange SA
 * SPDX-License-Identifier: MIT
 *
 * This software is distributed under the MIT license,
 * see the "LICENSE" file for more details
 * or https://spdx.org/licenses/MIT.html
 *
 * Authors: see CONTRIBUTORS.md
 */

#include "../iboran_application/iboran-application.h"
#include "iboran-ran-common.h"
#include "iboran-ran-params.h"

#include <ns3/applications-module.h>
#include <ns3/buildings-module.h>
#include <ns3/config-store.h>
#include <ns3/core-module.h>
#include <ns3/flow-monitor-module.h>
#include <ns3/internet-module.h>
#include <ns3/mobility-module.h>
#include <ns3/netanim-module.h>
#include <ns3/network-module.h>
#include <ns3/nr-module.h>
#include <ns3/point-to-point-module.h>
#include <ns3/three-gpp-channel-model.h>
#include <ns3/three-gpp-propagation-loss-model.h>
#include <ns3/three-gpp-spectrum-propagation-loss-model.h>

#include <filesystem>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("IbOranNrEnvironment");

namespace
{

/** Opt-in ib-ORAN wrapper for controlled LOS states; the stock model remains the delegate. */
class IbOranSelectiveConditionModel : public ChannelConditionModel
{
  public:
    static TypeId GetTypeId()
    {
        static TypeId tid = TypeId("ns3::IbOranSelectiveConditionModel")
                                .SetParent<ChannelConditionModel>()
                                .SetGroupName("IbOran")
                                .AddConstructor<IbOranSelectiveConditionModel>();
        return tid;
    }

    IbOranSelectiveConditionModel()
        : m_los(CreateObject<ChannelCondition>(ChannelCondition::LOS)),
          m_nlos(CreateObject<ChannelCondition>(ChannelCondition::NLOS))
    {
    }

    void Configure(Ptr<ChannelConditionModel> delegate,
                   Ptr<const MobilityModel> target,
                   bool selective)
    {
        m_delegate = delegate;
        m_target = target;
        m_selective = selective;
    }

    Ptr<ChannelCondition> GetChannelCondition(Ptr<const MobilityModel> a,
                                              Ptr<const MobilityModel> b) const override
    {
        if (m_selective && (a == m_target || b == m_target))
        {
            return m_nlos;
        }
        return m_los;
    }

    int64_t AssignStreams(int64_t stream) override
    {
        return m_delegate ? m_delegate->AssignStreams(stream) : 0;
    }

  private:
    Ptr<ChannelConditionModel> m_delegate;
    Ptr<const MobilityModel> m_target;
    Ptr<ChannelCondition> m_los;
    Ptr<ChannelCondition> m_nlos;
    bool m_selective{false};
};

NS_OBJECT_ENSURE_REGISTERED(IbOranSelectiveConditionModel);

void
LogChannelConditionSnapshot(Ptr<ChannelConditionModel> conditionModel,
                            NodeContainer ueNodes,
                            NodeContainer gnbNodes,
                            uint32_t sampleIndex)
{
    const auto gnbNode = gnbNodes.Get(0);
    const auto gnbMobility = gnbNode->GetObject<MobilityModel>();
    const auto gnbPosition = gnbMobility->GetPosition();
    for (uint32_t i = 0; i < ueNodes.GetN(); ++i)
    {
        const auto ueNode = ueNodes.Get(i);
        const auto ueMobility = ueNode->GetObject<MobilityModel>();
        const auto uePosition = ueMobility->GetPosition();
        const auto condition = conditionModel->GetChannelCondition(ueMobility, gnbMobility);
        const char* label = condition->GetLosCondition() == ChannelCondition::LOS ? "LOS" : "NLOS";
        std::cout << std::fixed << std::setprecision(6) << "CHANNEL_STATE,time_s="
                  << Simulator::Now().GetSeconds() << ",ue_node=" << ueNode->GetId()
                  << ",ue_index=" << (i + 1) << ",gnb_node=" << gnbNode->GetId()
                  << ",ue_position_m=" << uePosition.x << ':' << uePosition.y << ':'
                  << uePosition.z << ",gnb_position_m=" << gnbPosition.x << ':'
                  << gnbPosition.y << ':' << gnbPosition.z << ",condition=" << label << '\n';
    }
    if (sampleIndex < 20)
    {
        Simulator::Schedule(Seconds(1),
                            &LogChannelConditionSnapshot,
                            conditionModel,
                            ueNodes,
                            gnbNodes,
                            sampleIndex + 1);
    }
}

void
InstallSelectiveConditionModel(const CommonRanParams& commonParams,
                               OperationBandInfo& band,
                               NodeContainer& ueNodes,
                               NodeContainer& gnbNodes)
{
    const auto& mode = commonParams.channelConditionMode;
    if (mode == "default")
    {
        return;
    }
    if (mode != "all-los" && mode != "ue6-nlos")
    {
        throw std::invalid_argument("channelConditionMode must be default, all-los, or ue6-nlos");
    }
    if (mode == "ue6-nlos" &&
        (commonParams.channelConditionTargetUe == 0 ||
         commonParams.channelConditionTargetUe > ueNodes.GetN()))
    {
        throw std::invalid_argument("channelConditionTargetUe is outside the configured UE set");
    }

    const auto channel = band.GetBwpAt(0, 0)->GetChannel();
    const auto pathloss = DynamicCast<ThreeGppPropagationLossModel>(channel->GetPropagationLossModel());
    const auto spectrumLoss =
        DynamicCast<ThreeGppSpectrumPropagationLossModel>(channel->GetPhasedArraySpectrumPropagationLossModel());
    NS_ABORT_MSG_IF(!pathloss || !spectrumLoss,
                    "Selective condition requires the existing ThreeGpp pathloss and channel models");
    const auto threeGppChannel = DynamicCast<ThreeGppChannelModel>(spectrumLoss->GetChannelModel());
    NS_ABORT_MSG_IF(!threeGppChannel,
                    "Selective condition requires the existing ThreeGpp fading channel model");

    const auto original = pathloss->GetChannelConditionModel();
    NS_ABORT_MSG_IF(original != threeGppChannel->GetChannelConditionModel(),
                    "NR channel and pathloss do not share the same condition model");
    auto selective = CreateObject<IbOranSelectiveConditionModel>();
    const auto target = mode == "ue6-nlos"
                            ? ueNodes.Get(commonParams.channelConditionTargetUe - 1)
                                  ->GetObject<MobilityModel>()
                            : nullptr;
    selective->Configure(original, target, mode == "ue6-nlos");
    pathloss->SetChannelConditionModel(selective);
    threeGppChannel->SetChannelConditionModel(selective);

    NS_ABORT_MSG_IF(pathloss->GetChannelConditionModel() !=
                        threeGppChannel->GetChannelConditionModel(),
                    "Selective condition was not installed consistently in pathloss and channel models");
    std::cout << "CHANNEL_CONDITION_MODE=" << mode
              << ",target_ue_index=" << commonParams.channelConditionTargetUe
              << ",shared_condition_model=" << selective->GetInstanceTypeId().GetName() << '\n';
    Simulator::Schedule(Seconds(0),
                        &LogChannelConditionSnapshot,
                        selective,
                        ueNodes,
                        gnbNodes,
                        0);
}

} // namespace

// == NR-SPECIFIC SETUP FUNCTIONS ===============================================
void
SetupNrSpectrum(const NrParams& nrParams, Ptr<NrHelper> nrHelper, OperationBandInfo& band)
{
    // create operation band
    CcBwpCreator ccBwpCreator;
    CcBwpCreator::SimpleOperationBandConf bandConf;
    bandConf.m_centralFrequency = nrParams.centralFrequency;
    bandConf.m_channelBandwidth = nrParams.bandwidth;
    bandConf.m_numBwp = nrParams.numBwp;
    bandConf.m_numCc = nrParams.numCc;

    band = ccBwpCreator.CreateOperationBandContiguousCc(bandConf);
}

void
SetupNrChannelModel(Ptr<NrChannelHelper> channelHelper)
{
    channelHelper->ConfigureFactories("UMi", "Default", "ThreeGpp");
    Config::SetDefault("ns3::ThreeGppChannelModel::UpdatePeriod", TimeValue(MilliSeconds(0)));
    channelHelper->SetChannelConditionModelAttribute("UpdatePeriod", TimeValue(MilliSeconds(0)));
    channelHelper->SetPathlossAttribute("ShadowingEnabled", BooleanValue(true));
}

void
SetupNrBeamforming(const NrParams& nrParams, Ptr<NrHelper> nrHelper)
{
    Ptr<IdealBeamformingHelper> idealBeamformingHelper = CreateObject<IdealBeamformingHelper>();
    idealBeamformingHelper->SetAttribute("BeamformingMethod",
                                         TypeIdValue(DirectPathBeamforming::GetTypeId()));
    nrHelper->SetBeamformingHelper(idealBeamformingHelper);

    // antennas for all the UEs
    nrHelper->SetUeAntennaAttribute("NumRows", UintegerValue(nrParams.ueAntennaNumRows));
    nrHelper->SetUeAntennaAttribute("NumColumns", UintegerValue(nrParams.ueAntennaNumColumns));
    // nrHelper->SetUeAntennaAttribute("AntennaElement",
    //                 PointerValue(CreateObject<IsotropicAntennaModel>()));

    // antennas for all the gNBs
    nrHelper->SetGnbAntennaAttribute("NumRows", UintegerValue(nrParams.gNbAntennaNumRows));
    nrHelper->SetGnbAntennaAttribute("NumColumns", UintegerValue(nrParams.gNbAntennaNumColumns));
    // nrHelper->SetGnbAntennaAttribute("AntennaElement",
    //                 PointerValue(CreateObject<IsotropicAntennaModel>()));
}

void
SetupNrProtocolStack(const CommonRanParams& commonParams,
                     const NrParams& nrParams,
                     Ptr<NrHelper> nrHelper)
{
    // handover setup
    nrHelper->SetHandoverAlgorithmType("ns3::NrA3RsrpHandoverAlgorithm");

    // to avoid ping-pong effects due to signal fluctuations
    nrHelper->SetHandoverAlgorithmAttribute("Hysteresis",
                                            DoubleValue(commonParams.handoverHysteresis));
    nrHelper->SetHandoverAlgorithmAttribute(
        "TimeToTrigger",
        TimeValue(MilliSeconds(commonParams.handoverTimeToTrigger)));

    // MAC scheduler setup
    nrHelper->SetSchedulerTypeId(TypeId::LookupByName("ns3::IbOranNrMacScheduler"));

    std::cout << std::setw(30) << "NR protocol stack setup" << ": OK\n";
}

// == MAIN SIMULATOR ============================================================
int
main(int argc, char* argv[])
{
    SimParams& params = SimParams::GetInstance();
    params.SetRatType(RatType::NR);

    std::filesystem::path current_dir = std::filesystem::current_path();
    const char* runDir = std::getenv("IBORAN_RUN_DIR");
    const auto outputRoot = runDir ? std::filesystem::path(runDir)
                                   : current_dir / "contrib/iboran/notebook";
    params.LoadFromYaml((outputRoot / "logs/runConfig.yaml").string());

    params.Print(std::cout);

    auto& commonParams = params.GetCommonRanParams();
    auto& nrParams = params.GetNrParams();

    RngSeedManager::SetSeed(1);
    RngSeedManager::SetRun(commonParams.rngRun);

    // -- LTE AND EPC INITIALIZATION --------------------------------------------
    Ptr<NrHelper> nrHelper = CreateObject<NrHelper>();
    Ptr<NrPointToPointEpcHelper> epcHelper = CreateObject<NrPointToPointEpcHelper>();
    nrHelper->SetEpcHelper(epcHelper);

    // -- BACKHAUL SETUP --------------------------------------------------------
    std::cout << "\n-- Backhaul Setup ---------------------" << std::endl;

    // create the PGW node
    Ptr<Node> pgw = epcHelper->GetPgwNode();

    // create the SGW and MME nodes (for now, just to set mobility modes)
    Ptr<Node> sgw = epcHelper->GetSgwNode();
    Ptr<Node> mme = NodeList::GetNode(2); // internally created as 3rd node

    // create the Remote Host (internet server)
    NodeContainer remoteHostContainer;
    remoteHostContainer.Create(commonParams.remoteHostNum);
    Ptr<Node> remoteHost = remoteHostContainer.Get(0);

    InternetStackHelper internet;
    internet.Install(remoteHostContainer);

    // setup backhaul nodes mobility
    SetupBackhaulMobility(commonParams, pgw, sgw, mme, remoteHost);

    std::cout << std::left << std::setw(30) << "PGW ID" << ": " << pgw->GetId() << "\n"
              << std::setw(30) << "SGW ID" << ": " << sgw->GetId() << "\n"
              << std::setw(30) << "MME ID" << ": " << mme->GetId() << "\n"
              << std::setw(30) << "Remote Host ID" << ": " << remoteHost->GetId() << std::endl;

    // create p2p backhaul link
    PointToPointHelper p2ph;
    p2ph.SetDeviceAttribute("DataRate", DataRateValue(commonParams.backhaulDataRate));
    p2ph.SetDeviceAttribute("Mtu", UintegerValue(commonParams.backhaulMtu));
    p2ph.SetChannelAttribute("Delay", TimeValue(MilliSeconds(commonParams.backhaulDelay)));
    NetDeviceContainer internetDevices = p2ph.Install(pgw, remoteHost);

    std::cout << std::setw(30) << "Ethernet link setup" << ": OK" << std::endl;

    // assign IP address
    Ipv4AddressHelper ipv4h;
    ipv4h.SetBase("1.0.0.0", "255.0.0.0");
    Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign(internetDevices);
    Ipv4Address pgwAddr = internetIpIfaces.GetAddress(0 // PGW interface = 0 -> IP: 1.0.0.1
    );
    Ipv4Address remoteHostAddr =
        internetIpIfaces.GetAddress(1 // RemoteHost interface = 1 -> IP: 1.0.0.2
        );

    std::cout << std::setw(30) << "PGW IP address" << ": " << pgwAddr << "\n"
              << std::setw(30) << "Remote Host IP address" << ": " << remoteHostAddr << std::endl;

    // set up the static routing for the Remote Host
    Ipv4StaticRoutingHelper ipv4RoutingHelper;
    Ptr<Ipv4StaticRouting> remoteHostStaticRouting =
        ipv4RoutingHelper.GetStaticRouting(remoteHost->GetObject<Ipv4>());
    remoteHostStaticRouting->SetDefaultRoute(pgwAddr, 1 // via PGW (Remote Host interface = 1)
    );

    std::cout << std::setw(30) << "Static routing setup" << ": OK" << std::endl;

    // -- NR FRONTHAUL SETUP ---------------------------------------------------
    std::cout << "\n-- NR Fronthaul Setup -----------------" << std::endl;

    // define nodes configuration
    NodeContainer gnbNodes;
    NodeContainer ueNodes;
    gnbNodes.Create(commonParams.xnbNum);
    ueNodes.Create(commonParams.ueNum);

    std::cout << std::left << std::setw(30) << "gNB ID" << ": " << gnbNodes.Get(0)->GetId() << "\n";
    for (uint32_t ueCount = 0; ueCount < ueNodes.GetN(); ++ueCount)
    {
        Ptr<Node> ue = ueNodes.Get(ueCount);
        std::stringstream labelStream;
        labelStream << "UE " << ueCount + 1 << " ID";
        std::cout << std::setw(30) << labelStream.str() << ": " << ue->GetId() << "\n";
    }

    // setup fronthaul nodes mobility
    SetupFronthaulMobility(commonParams, params.GetRatType(), gnbNodes, ueNodes);

    // create one operational band with one bandwidth part
    OperationBandInfo band;
    SetupNrSpectrum(nrParams, nrHelper, band);

    // setup channel model and beamforming
    Ptr<NrChannelHelper> channelHelper = CreateObject<NrChannelHelper>();
    SetupNrChannelModel(channelHelper);
    channelHelper->AssignChannelsToBands({band});
    InstallSelectiveConditionModel(commonParams, band, ueNodes, gnbNodes);

    BandwidthPartInfoPtrVector allBwps = CcBwpCreator::GetAllBwps({band});

    // initialize operation band with all BWPs
    for (auto it = allBwps.begin(); it != allBwps.end(); ++it)
    {
        (*it).get()->m_channelBandwidth = nrParams.bandwidth / nrParams.numBwp;
    }

    SetupNrBeamforming(nrParams, nrHelper);
    SetupNrProtocolStack(commonParams, nrParams, nrHelper);

    nrHelper->SetGnbPhyAttribute("Numerology", UintegerValue(nrParams.numerology));
    nrHelper->SetGnbPhyAttribute("Pattern", StringValue(nrParams.tddPattern));
    nrHelper->SetGnbPhyAttribute("TxPower", DoubleValue(commonParams.xnbTxPower));

    nrHelper->SetUePhyAttribute("TxPower", DoubleValue(commonParams.ueMaxTxPower));

    // create devices and install them in the nodes
    NetDeviceContainer gnbDevs;
    NetDeviceContainer ueDevs;
    gnbDevs = nrHelper->InstallGnbDevice(gnbNodes, allBwps);
    ueDevs = nrHelper->InstallUeDevice(ueNodes, allBwps);

    // install the IP stack on the UEs
    internet.Install(ueNodes);
    Ipv4InterfaceContainer ueIpIfaces;
    ueIpIfaces = epcHelper->AssignUeIpv4Address(NetDeviceContainer(ueDevs));

    std::cout << std::setw(30) << "Node device setup" << ": OK" << std::endl;

    // assign IP address to UEs and set the default gateway
    std::cout << std::setw(30) << "Gateway IP address" << ": " << pgwAddr << std::endl;
    for (uint32_t ueCount = 0; ueCount < ueNodes.GetN(); ++ueCount)
    {
        Ptr<Node> ue = ueNodes.Get(ueCount);
        // set the default gateway for the UE
        Ptr<Ipv4StaticRouting> ueStaticRouting =
            ipv4RoutingHelper.GetStaticRouting(ue->GetObject<Ipv4>());
        ueStaticRouting->SetDefaultRoute(epcHelper->GetUeDefaultGatewayAddress(), 1);
        std::stringstream labelStream;
        labelStream << "UE " << ueCount + 1 << " IP address";
        std::cout << std::setw(30) << labelStream.str() << ": " << ueIpIfaces.GetAddress(ueCount)
                  << "\n";
    }

    // attach UEs to gNB
    // nrHelper->AttachToClosestGnb(ueDevs, gnbDevs);
    for (uint32_t ueCount = 0; ueCount < ueDevs.GetN(); ++ueCount)
    {
        nrHelper->AttachToGnb(ueDevs.Get(ueCount), gnbDevs.Get(0));
    }

    std::cout << std::setw(30) << "UE attachement to gNB" << ": OK" << std::endl;

    // -- APPLICATION SETUP ----------------------------------------------------
    ApplicationContainer txApps;
    ApplicationContainer rxApps;
    SetupIbOranApplications(commonParams,
                            params.GetRatType(),
                            ueNodes,
                            remoteHost,
                            ueIpIfaces,
                            remoteHostAddr,
                            txApps,
                            rxApps,
                            ueDevs);

    std::cout << std::setw(30) << "Application setup" << ": OK" << std::endl;

    // -- LOGGING & TRACING SETUP ----------------------------------------------
    std::cout << "\n-- Tracing & Logging ------------------" << std::endl;

    if (commonParams.enableIbOranSchedCoreLog)
    {
        LogComponentEnable("IbOranSchedCore", LOG_LEVEL_INFO);
    }

    if (commonParams.enableRrcLog)
    {
        LogComponentEnable("NrUeRrc", LOG_LEVEL_INFO);
        LogComponentEnable("NrGnbRrc", LOG_LEVEL_INFO);
    }

    nrHelper->EnableTraces();

    // flow monitor setup
    FlowMonitorHelper flowHelper;
    Ptr<FlowMonitor> flowMonitor = flowHelper.InstallAll();

    // netanim setup
    AnimationInterface* anim = commonParams.enableNetAnim && !runDir
                                   ? SetupNetAnim(commonParams, params.GetRatType(), remoteHost,
                                                  pgw, sgw, mme, gnbNodes, ueNodes,
                                                  "iboran-nr-anim.xml")
                                   : nullptr;

    // -- SIMULATION RUN -------------------------------------------------------
    std::cout << "ib-ORAN NR Environment: Running..." << std::endl;
    Simulator::Stop(Seconds(commonParams.simTime));
    Simulator::Run();

    PrintApplicationStats(commonParams, params.GetRatType(), ueNodes, txApps, rxApps);

    // save flow monitor stats
    std::filesystem::path stats_dir = outputRoot / ".flowstats";
    std::filesystem::create_directories(stats_dir);
    std::filesystem::path stats_path = stats_dir / "iboran-flowstats.xml";
    flowMonitor->SerializeToXmlFile(stats_path.string(), true, true);

    std::cout << "\nib-ORAN NR Environment: Run finished.\n";

    delete anim;
    anim = nullptr;

    Simulator::Destroy();

    return 0;

} // end main
