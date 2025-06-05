from fastapi import APIRouter, Body, HTTPException, Request

from config import plugin_config
from src.plugin_sdk.controller import PluginController
from src.plugin_sdk.registry import PluginRegistry

from .core.response_models import StandardResponse
from .middlewares.config_manager import ConfigManager

# Initialize registry and auto-discover methods
registry = PluginRegistry()
registry.auto_discover("src.providers")

# Initialize controller
controller = PluginController(registry)

router = APIRouter()


@router.get("/version")
async def get_version():
    """Return current version of the plugin"""
    return {**plugin_config}


@router.post("/version")
async def update_version(config: dict = Body(...)):
    """Update plugin configuration"""
    config_manager = ConfigManager()
    if config_manager.save_config(config):
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "data": config_manager.get_config(),
        }
    raise HTTPException(status_code=500, detail="Failed to update configuration")


@router.get("/methods", response_model=StandardResponse)
async def get_methods():
    """Return list of available methods"""
    return {
        "status": "success",
        "data": registry.get_all_methods(),
        "message": "Available methods retrieved successfully",
    }


@router.get("/method/{method_name}")
async def get_method_config(method_name: str):
    """Return configuration for specific method"""
    try:
        method_config = registry.get_method_config(method_name)

        return {
            "status": "success",
            "data": method_config,
            "message": f"Configuration for {method_name} retrieved successfully",
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Method not found")


@router.post("/method/{method_name}", response_model=StandardResponse)
async def execute_method(method_name: str, request: Request):
    """Execute a method based on its name"""
    try:
        data = await request.json() if await request.body() else {}
        result = await controller.execute(method_name, data)

        return {
            "status": "success",
            "data": result,
            "message": f"Executed {method_name} successfully",
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {"error": str(e)},
            "message": f"Execution of {method_name} failed: {str(e)}",
        }
