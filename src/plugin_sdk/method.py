from typing import Any, Callable, Dict, List, Optional, Type

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field, create_model

from src.api.middlewares.config_manager import ConfigManager
from src.config import BASE_URLS


class ParameterDefinition(BaseModel):
    """Definition of a method parameter"""

    name: str
    type: str  # string, number, boolean, array, etc.
    required: bool = False
    description: str = ""
    default: Any = None
    validation: Dict[str, Any] = Field(default_factory=dict)  # regex, min, max, etc.
    options: List[Dict[str, str]] = Field(default_factory=list)  # For dropdowns/selects


class MethodMetadata(BaseModel):
    """Metadata for a plugin method"""

    name: str
    title: str
    description: str
    parameters: List[ParameterDefinition] = Field(default_factory=list)


class ApiEndpoint(BaseModel):
    """Definition of an external API endpoint"""

    url: str  # can be a *path* like "/repos/{owner}/{repo}"
    provider: Optional[str] = None
    method: str = "GET"
    headers: Dict[str, str] = Field(default_factory=dict)
    query_param_mapping: Dict[str, str] = Field(default_factory=dict)
    body_mapping: Dict[str, str] = Field(default_factory=dict)
    response_mapping: Dict[str, str] = Field(default_factory=dict)


class PluginMethod:
    """Base class for defining plugin methods"""

    def __init__(
        self,
        metadata: MethodMetadata,
        endpoint: ApiEndpoint,
        pre_process: Optional[Callable] = None,
        post_process: Optional[Callable] = None,
    ):
        self.metadata = metadata
        self.endpoint = endpoint
        self.pre_process = pre_process
        self.post_process = post_process

        # Create a pydantic model for validating parameters
        fields = {}
        for param in metadata.parameters:
            field_type = self._get_field_type(param.type)
            field_kwargs = {
                "description": param.description,
                "default": param.default if not param.required else ...,
            }
            # Add validation rules
            for rule, value in param.validation.items():
                field_kwargs[rule] = value

            fields[param.name] = (field_type, Field(**field_kwargs))

        self.params_model = create_model(f"{metadata.name}Params", **fields)

    def _get_field_type(self, param_type: str) -> Type:
        """Convert string type to actual Python type"""
        type_map = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": List,
            "object": Dict,
        }
        base_type = type_map.get(param_type.rstrip("[]"), str)

        if param_type.endswith("[]"):
            return List[base_type]
        return base_type

    async def execute(self, raw_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the method with the given parameters"""
        try:
            # Validate parameters using the generated model
            validated_params = self.params_model(**raw_params)

            # Pre-process parameters if needed
            processed_params = validated_params.dict()
            if self.pre_process:
                processed_params = self.pre_process(processed_params)

            # Build request to external API
            request_data = self._build_request(processed_params)

            # Execute API call
            response = await self._call_api(request_data)

            # Post-process response if needed
            if self.post_process:
                response = self.post_process(response)

            return response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error executing {self.metadata.name}: {str(e)}",
            )

    def _build_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build the request to the external API based on parameter mappings"""
        # Format URL template with parameters (supports placeholders like {param})
        try:
            if self.endpoint.provider:
                base = BASE_URLS[self.endpoint.provider]
                url = base + self.endpoint.url.format(**params)
            else:
                url = self.endpoint.url.format(**params)
        except Exception:
            url = self.endpoint.url

        # Implementation details for mapping params to API request
        query_params = {}
        body = {}

        # Map query parameters
        for param_name, api_param in self.endpoint.query_param_mapping.items():
            if param_name in params:
                query_params[api_param] = params[param_name]

        # Map body parameters
        for param_name, api_param in self.endpoint.body_mapping.items():
            if param_name in params:
                # Handle nested parameters with dot notation
                if "." in api_param:
                    self._set_nested_value(
                        body, api_param.split("."), params[param_name]
                    )
                else:
                    body[api_param] = params[param_name]

        return {
            "url": url,
            "method": self.endpoint.method,
            "headers": self.endpoint.headers,
            "query_params": query_params,
            "body": body,
        }

    def _set_nested_value(self, obj: Dict, path: List[str], value: Any):
        """Set a value in a nested dictionary using a path"""
        for i, key in enumerate(path):
            if i == len(path) - 1:
                obj[key] = value
            else:
                if key not in obj:
                    obj[key] = {}
                obj = obj[key]

    async def _call_api(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make the actual API call using httpx"""
        try:
            # Get credentials from ConfigManager
            config_manager = ConfigManager()
            creds = config_manager.get_api_credentials(provider=self.endpoint.provider)

            # Merge credentials with endpoint headers
            headers = {**request_data["headers"], **creds}

            # Set up the request parameters
            url = request_data["url"]
            method = request_data["method"]
            query_params = request_data.get("query_params", {})
            body = request_data.get("body", {})

            # Make the API call asynchronously
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(
                        url, params=query_params, headers=headers
                    )
                elif method.upper() == "POST":
                    response = await client.post(
                        url, params=query_params, json=body, headers=headers
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url, params=query_params, json=body, headers=headers
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(
                        url, params=query_params, headers=headers
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Check for HTTP errors
                response.raise_for_status()

                # Return the JSON response
                return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API Error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request Error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calling API: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for this method for the UI"""
        return {
            "name": self.metadata.name,
            "title": self.metadata.title,
            "description": self.metadata.description,
            "params": [
                {
                    "key": param.name,
                    "title": param.name.title(),
                    "description": param.description,
                    "attr": {
                        "input_type": param.type,
                        "required": param.required,
                        "regex_pattern": param.validation.get("regex_pattern"),
                        "secret": False,
                    },
                    "placeholder": f"Enter {param.name}",
                    "value": [param.default] if param.default is not None else [],
                    "options": param.options,
                }
                for param in self.metadata.parameters
            ],
        }
