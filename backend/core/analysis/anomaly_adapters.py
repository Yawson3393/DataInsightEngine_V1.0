"""
Anomaly detection plugin — supports simple rule-based scores
and placeholder for ML-based detectors.
"""

import numpy as np
from typing import Dict, Any
from .base import AnalysisPlugin
from .registry import registry


@registry.register
class AnomalyDetectorPlugin(AnalysisPlugin):
    name = "anomaly_detector"
    plugin_type = "anomaly"

    def run(self, aligned: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:

        out = {}

        temp_threshold = config.get("TEMP_DIFF_THRESHOLD", 2)
        volt_low = config.get("VOLT_DISCHARGE_CUTOFF", 2800)
        volt_high = config.get("VOLT_CHARGE_CUTOFF", 3650)

        for rack_id, rack in aligned["rack"].items():
            rack_anom = []

            for mod_id, mod in rack["modules"].items():
                temp = np.array(mod["temp"])     # T × Ncells
                volt = np.array(mod["voltage"])  # T × Ncells

                # --- temperature spread anomaly ---
                tmax = np.nanmax(temp, axis=1)
                tmin = np.nanmin(temp, axis=1)
                temp_spread = tmax - tmin
                bad_temp = np.where(temp_spread > temp_threshold)[0].tolist()

                # --- voltage bounding anomaly ---
                bad_v_low = np.where(volt < volt_low)[0].tolist()
                bad_v_high = np.where(volt > volt_high)[0].tolist()

                rack_anom.append({
                    "module_id": mod_id,
                    "high_temp_spread_idx": bad_temp,
                    "volt_low_idx": bad_v_low,
                    "volt_high_idx": bad_v_high
                })

            out[rack_id] = rack_anom

        return out
