"""
SOH / EOL estimation plugin.
This is a light-weight proxy; real projects may replace this with AI model.

SOH proxy uses:
- capacity fade (via mean voltage)
- resistance proxy (via dv/dt)
"""

import numpy as np
from typing import Dict, Any
from .base import AnalysisPlugin
from .registry import registry


@registry.register
class SOHProxyPlugin(AnalysisPlugin):
    name = "soh_proxy"
    plugin_type = "soh"

    def run(self, aligned: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:

        result = {}

        for rack_id, rack in aligned["rack"].items():
            rack_out = {}

            for mod_id, mod in rack["modules"].items():
                volt = np.array(mod["voltage"])
                dvdt = np.gradient(volt, axis=0)

                v_mean = np.nanmean(volt, axis=1)
                dvdt_mean = np.nanmean(dvdt, axis=1)

                # Simple heuristics
                soh_cap = (v_mean - np.min(v_mean)) / (np.max(v_mean) - np.min(v_mean) + 1e-6)
                soh_res = np.tanh(1 / (np.abs(dvdt_mean) + 1e-6))

                rack_out[mod_id] = {
                    "soh_capacity": soh_cap.mean().item(),
                    "soh_resistance": soh_res.mean().item(),
                }

            result[rack_id] = rack_out

        return result
