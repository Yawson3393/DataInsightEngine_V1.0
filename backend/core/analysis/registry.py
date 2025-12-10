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

# -----------------------------------------------------
# Auto-discovery: load all plugins in analysis package
# -----------------------------------------------------
import pkgutil
import importlib
import os

def load_plugins():
    """
    自动扫描 analysis/ 目录下所有 .py 文件并导入；
    当文件被导入时，其中的 @registry.register 的插件类自动注册。
    """
    pkg_dir = os.path.dirname(__file__)

    for _, module_name, is_pkg in pkgutil.iter_modules([pkg_dir]):
        # 跳过子包与 __init__
        if is_pkg or module_name.startswith("_"):
            continue

        # 如：analysis.cell_features
        full_name = f"{__package__}.{module_name}"

        try:
            importlib.import_module(full_name)
        except Exception as e:
            print(f"[WARN] load_plugins: failed loading {full_name}: {e}")

# global registry
registry = AnalysisRegistry()
