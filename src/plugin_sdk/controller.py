from typing import Dict, Any
from fastapi import HTTPException
from src.plugin_sdk.registry import PluginRegistry


class PluginController:
    """Controller for executing plugin methods"""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    async def execute(self, method_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a method with the given data"""
        try:
            method = self.registry.get_method(method_name)
            result = await method.execute(data)
            return result
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log the error and raise a generic HTTP exception
            print(f"Error executing {method_name}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to execute {method_name}: {str(e)}"
            )
