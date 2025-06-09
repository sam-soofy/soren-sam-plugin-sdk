import json
import os
from typing import Any, Dict, Optional

from src.config import plugin_config


class ConfigManager:
    _instance = None
    _config_file = "plugin_runtime_config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return plugin_config.copy()

    def save_config(self, new_config: Dict[str, Any]) -> bool:
        try:
            with open(self._config_file, "w") as f:
                json.dump(new_config, f, indent=2)
            self.config = new_config
            return True
        except Exception:
            return False

    def get_api_credentials(self, provider: Optional[str] = None) -> Dict[str, str]:
        # find the init_config section with name == provider
        section = next(
            cfg for cfg in self.config["init_config"] if cfg["name"] == provider
        )
        token = section["params"][0]["value"][0]  # your PAT
        return {"Authorization": f"Bearer {token}"} if token else {}

    def get_config(self) -> Dict[str, Any]:
        return self.config
