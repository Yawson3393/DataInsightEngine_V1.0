# 分析插件注册器（entry-points like）
"""
Registry: plugin loader and execution manager.
Allows dynamic registering of analysis plugins.
"""

from typing import Dict, Type, List
from .base import AnalysisPlugin


class AnalysisRegistry:

    def __init__(self):
        self._plugins: Dict[str, Type[AnalysisPlugin]] = {}

    # -----------------------------------------------------
    # Register plugin class
    # -----------------------------------------------------
    def register(self, plugin_cls: Type[AnalysisPlugin]):
        if not issubclass(plugin_cls, AnalysisPlugin):
            raise TypeError("Plugin must inherit AnalysisPlugin")
        self._plugins[plugin_cls.name] = plugin_cls
        return plugin_cls

    # -----------------------------------------------------
    # Instantiate plugin
    # -----------------------------------------------------
    def create(self, name: str) -> AnalysisPlugin:
        if name not in self._plugins:
            raise KeyError(f"Unknown plugin: {name}")
        return self._plugins[name]()

    # -----------------------------------------------------
    # List available plugins
    # -----------------------------------------------------
    def list_plugins(self) -> List[str]:
        return list(self._plugins.keys())

    # -----------------------------------------------------
    # Execute all plugins
    # -----------------------------------------------------
    def run_all(self, aligned, config):
        results = {}
        for name, pcls in self._plugins.items():
            plugin = pcls()
            output = plugin.run(aligned, config)
            results[name] = output
        return results


# global registry
registry = AnalysisRegistry()
