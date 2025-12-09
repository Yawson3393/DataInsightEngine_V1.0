# 分析插件基类（接口定义）
"""
Base analysis plugin — all analysis modules derive from this.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class AnalysisPlugin(ABC):
    """
    Base class for analysis plugins. A plugin processes part
    of the day's aligned data and generates derived results.
    """

    name: str = "base_plugin"
    plugin_type: str = "generic"  # "cell", "anomaly", "soh", etc.

    @abstractmethod
    def run(self, aligned: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform an analysis step.

        Parameters
        ----------
        aligned: dict
            Aligned, structured dataset (bank → racks → modules → cells)
        config: dict
            Configuration parameters from settings

        Returns
        -------
        dict
            Structured result to be merged into analysis result tree
        """
        pass

    def __repr__(self):
        return f"<AnalysisPlugin {self.name} ({self.plugin_type})>"
