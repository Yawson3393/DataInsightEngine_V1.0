"""
Cell-level feature extraction:
- voltage stats
- temperature stats
- dV/dt dynamic
- balance / inconsistency
- heat map projections
"""

import numpy as np
from typing import Dict, Any
from .base import AnalysisPlugin
from .registry import registry


@registry.register
class CellFeaturePlugin(AnalysisPlugin):
    name = "cell_features"
    plugin_type = "cell"

    def run(self, aligned: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        aligned structure:
          aligned["rack"][rack_id]["modules"][module_id]["voltage"][cell_index]
          aligned["rack"][rack_id]["modules"][module_id]["temp"][cell_index]
        """

        result = {}

        for rack_id, rack in aligned["rack"].items():
            rack_out = {}
            for mod_id, mod in rack["modules"].items():

                volt = np.array(mod["voltage"])       # shape: (T, Ncells)
                temp = np.array(mod["temp"])          # shape: (T, Ncells)

                # --- basic statistics ---
                v_mean = np.nanmean(volt, axis=0)
                v_std = np.nanstd(volt, axis=0)
                v_min = np.nanmin(volt, axis=0)
                v_max = np.nanmax(volt, axis=0)

                t_mean = np.nanmean(temp, axis=0)
                t_std = np.nanstd(temp, axis=0)

                # --- dynamics ---
                dvdt = np.gradient(volt, axis=0)
                dvdt_mean = np.nanmean(dvdt, axis=0)
                dvdt_std = np.nanstd(dvdt, axis=0)

                rack_out[mod_id] = {
                    "v_mean": v_mean.tolist(),
                    "v_std": v_std.tolist(),
                    "v_min": v_min.tolist(),
                    "v_max": v_max.tolist(),
                    "t_mean": t_mean.tolist(),
                    "t_std": t_std.tolist(),
                    "dvdt_mean": dvdt_mean.tolist(),
                    "dvdt_std": dvdt_std.tolist(),
                }

            result[rack_id] = rack_out

        return result
