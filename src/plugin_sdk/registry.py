import importlib
import pkgutil
from typing import Any, Dict, List

from src.api.middlewares.config_manager import ConfigManager
from src.plugin_sdk.method import PluginMethod


class PluginRegistry:
    """Registry for plugin methods"""

    def __init__(self):
        self.methods: Dict[str, PluginMethod] = {}
        self.config_manager = ConfigManager()

    def register(self, method: PluginMethod):
        """Register a method"""
        self.methods[method.metadata.name] = method

    def get_method(self, name: str) -> PluginMethod:
        """Get a method by name"""
        if name not in self.methods:
            raise ValueError(f"Method '{name}' not found")
        return self.methods[name]

    def get_all_methods(self) -> List[Dict[str, Any]]:
        """Get list of all registered methods with their metadata"""
        return [
            {
                "method": name,
                "title": method.metadata.title,
                "description": method.metadata.description,
            }
            for name, method in self.methods.items()
        ]

    def get_method_config(self, name: str) -> Dict[str, Any]:
        """Get configuration for a specific method"""
        method = self.get_method(name)
        return method.get_config()

    def auto_discover(self, package_name: str):
        """Recursively auto-discover and register PluginMethod instances in the given package"""
        try:
            package = importlib.import_module(package_name)

        except ImportError:
            return

        for finder, name, is_pkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            if is_pkg:
                continue
            try:
                module = importlib.import_module(name)
            except Exception:
                continue
            for attr in vars(module).values():
                if isinstance(attr, PluginMethod):
                    self.register(attr)

    def initialize_plugin(
        self, plugin_name: str, plugin_config: Dict[str, Any]
    ) -> bool:
        """Initialize a plugin with configuration"""
        # Update the config in ConfigManager
        config = self.config_manager.get_config()

        # Update plugin specific config if it exists
        config["name"] = plugin_config.get("name", plugin_name)
        config["author"] = plugin_config.get("author", "")
        config["version"] = plugin_config.get("version", "v1.0.0")
        config["init_config"] = plugin_config.get("init_config", [])

        # Save the updated config
        return self.config_manager.save_config(config)
