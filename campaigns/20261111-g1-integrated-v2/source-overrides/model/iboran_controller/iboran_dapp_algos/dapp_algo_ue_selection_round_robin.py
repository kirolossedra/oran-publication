# Software Name: ib-ORAN
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: MIT
#
# This software is distributed under the MIT license,
# see the "LICENSE" file for more details
# or https://spdx.org/licenses/MIT.html
#
# Authors: see CONTRIBUTORS.md

from .dapp_algo_ue_selection import DAppAlgoUeSelection


class DAppAlgoUeSelectionRoundRobin(DAppAlgoUeSelection):
    _ID_PREFIX = "RoundRobin"

    def __init__(self, k, intents, rat_type):
        super().__init__(k, intents, rat_type, algo_id=self._ID_PREFIX)
        self._reset_variables()

    def process(self, candidates, e3Indication, e2DAppControl, **kwargs) -> bool:
        """Prioritize never-served candidates, then least recently served."""
        history = kwargs.get("_hist_link_rnti_subframe", {}).get(
            e3Indication.linkDirection, {}
        )
        self.selected_idx_k = sorted(
            candidates,
            key=lambda idx: (
                history.get(e3Indication.ue[idx].rnti, -1),
                int(e3Indication.ue[idx].rnti),
            ),
        )[: self.k]
        return True
