# analysis/compute_features.py
"""
Bridge: compute_battery_features
Calls the AnalysisRegistry.run_all to execute all registered plugins.
"""

from typing import Dict, Any
from .registry import registry
from ..logging_cfg import get_task_logger

log = get_task_logger("compute_features")


def compute_battery_features(aligned: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run all registered analysis plugins on `aligned` data and return a dict
    mapping plugin_name -> plugin_result.
    """
    cfg = config or {}
    try:
        log.info("compute_battery_features: running registry.run_all")
        results = registry.run_all(aligned, cfg)
        log.info(f"compute_battery_features: finished, plugins={list(results.keys())}")
        return results
    except Exception as e:
        log.exception("compute_battery_features failed")
        # propagate exception so worker can mark job as failed and record traceback
        raise
