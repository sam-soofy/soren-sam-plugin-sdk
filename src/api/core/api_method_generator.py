"""
API Method Generator

This module provides utilities for generating API method classes from OpenAPI specifications.
It can be used to quickly scaffold new plugins that interface with external APIs.
"""

import json
import re
from typing import Any, Dict, List

# Handle optional yaml dependency gracefully
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class OpenApiParser:
    """Parser for OpenAPI specifications to generate API method classes."""

    def __init__(self, spec_path: str):
        """Initialize the parser with the path to an OpenAPI specification file."""
        self.spec_path = spec_path
        self.spec = self._load_spec()

    def _load_spec(self) -> Dict[str, Any]:
        """Load the OpenAPI specification from a file."""
        try:
            with open(self.spec_path, "r") as f:
                if self.spec_path.endswith(".json"):
                    return json.load(f)
                elif self.spec_path.endswith((".yaml", ".yml")):
                    if not YAML_AVAILABLE:
                        raise ImportError(
                            "PyYAML is required to parse YAML files. Install it with: pip install pyyaml"
                        )
                    return yaml.safe_load(f)
                else:
                    raise ValueError(
                        f"Unsupported file format: {self.spec_path}. Use JSON or YAML."
                    )
        except FileNotFoundError:
            raise FileNotFoundError(
                f"OpenAPI specification file not found: {self.spec_path}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in specification file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load OpenAPI spec: {str(e)}")

    def generate_api_methods(self, output_path: str, base_url_var: str = "BASE_URL"):
        """Generate API method classes from the OpenAPI specification."""
        endpoints = self._extract_endpoints()

        # Generate the Python code
        code = self._generate_code(endpoints, base_url_var)

        # Write the code to the output file
        with open(output_path, "w") as f:
            f.write(code)

        return f"Generated {len(endpoints)} API methods in {output_path}"

    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """Extract endpoints from the OpenAPI specification."""
        endpoints = []

        paths = self.spec.get("paths", {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ("get", "post", "put", "delete", "patch"):
                    continue

                endpoint = {
                    "path": path,
                    "method": method.upper(),
                    "operation_id": operation.get("operationId", ""),
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "parameters": operation.get("parameters", []),
                    "request_body": operation.get("requestBody", {}),
                    "responses": operation.get("responses", {}),
                }

                # Generate a class name if operationId is not provided
                if not endpoint["operation_id"]:
                    endpoint["operation_id"] = self._generate_operation_id(path, method)

                endpoints.append(endpoint)

        return endpoints

    def _generate_operation_id(self, path: str, method: str) -> str:
        """Generate an operation ID from the path and method."""
        # Remove path parameters
        path = re.sub(r"{([^}]+)}", r"\1", path)

        # Split the path and remove empty segments
        segments = [s for s in path.split("/") if s]

        # Create a camel case name
        name = "".join(s.title() for s in segments)

        # Add the method
        return f"{method.lower()}{name}"

    def _generate_code(self, endpoints: List[Dict[str, Any]], base_url_var: str) -> str:
        """Generate Python code for the API method classes."""
        if not endpoints:
            raise ValueError("No endpoints found in the OpenAPI specification")

        # Start with imports and base class
        code = [
            '"""',
            "Generated API Methods",
            "",
            "This module contains API method classes generated from an OpenAPI specification.",
            '"""',
            "",
            "import requests",
            "from typing import Dict, Any, List",
            "from fastapi import HTTPException",
            "",
            "",
            "class ApiMethod:",
            '    """Base class for API methods that handles common functionality."""',
            "    ",
            '    def __init__(self, endpoint: str, method: str = "GET"):',
            "        self.endpoint = endpoint",
            "        self.method = method",
            f"        self.base_url = {base_url_var}",
            "        ",
            "    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:",
            '        """Validate and transform input parameters."""',
            "        return params",
            "        ",
            "    def transform_response(self, response: requests.Response) -> Dict[str, Any]:",
            '        """Transform the API response to the expected format."""',
            "        if response.status_code == 204:",
            "            return {",
            '                "status_code": 204,',
            '                "status": "success",',
            '                "message": "No content, but operation was successful",',
            "            }",
            "            ",
            "        response.raise_for_status()",
            "        return response.json()",
            "    ",
            "    def execute(self, **kwargs) -> Dict[str, Any]:",
            '        """Execute the API call with validated parameters."""',
            "        try:",
            "            params = self.validate_params(kwargs)",
            "            ",
            '            if self.method == "GET":',
            "                response = requests.get(",
            '                    f"{self.base_url}/{self.endpoint}",',
            "                    headers=get_headers(),",
            '                    params=params.get("query_params", {}),',
            "                    timeout=30",
            "                )",
            '            elif self.method == "POST":',
            "                response = requests.post(",
            '                    f"{self.base_url}/{self.endpoint}",',
            "                    headers=get_headers(),",
            '                    json=params.get("body", {}),',
            "                    timeout=30",
            "                )",
            '            elif self.method == "PUT":',
            "                response = requests.put(",
            '                    f"{self.base_url}/{self.endpoint}",',
            "                    headers=get_headers(),",
            '                    json=params.get("body", {}),',
            "                    timeout=30",
            "                )",
            '            elif self.method == "DELETE":',
            "                response = requests.delete(",
            '                    f"{self.base_url}/{self.endpoint}",',
            "                    headers=get_headers(),",
            '                    json=params.get("body", {}),',
            "                    timeout=30",
            "                )",
            '            elif self.method == "PATCH":',
            "                response = requests.patch(",
            '                    f"{self.base_url}/{self.endpoint}",',
            "                    headers=get_headers(),",
            '                    json=params.get("body", {}),',
            "                    timeout=30",
            "                )",
            "            else:",
            '                raise ValueError(f"Unsupported HTTP method: {self.method}")',
            "                ",
            "            return self.transform_response(response)",
            "        except Exception as e:",
            "            raise HTTPException(",
            "                status_code=500, ",
            '                detail=f"Failed to execute {self.__class__.__name__}: {str(e)}"',
            "            ) from e",
            "",
        ]

        # Add each API method class
        for endpoint in endpoints:
            class_name = self._to_class_name(endpoint["operation_id"])
            method = endpoint["method"]
            path = endpoint["path"]
            description = (
                endpoint["description"] or endpoint["summary"] or f"{method} {path}"
            )

            # Extract path parameters
            path_params = re.findall(r"{([^}]+)}", path)

            # Replace path parameters with format placeholders
            formatted_path = re.sub(r"{([^}]+)}", r"{\1}", path.lstrip("/"))

            class_code = [
                "",
                f"class {class_name}(ApiMethod):",
                f'    """{description}"""',
                "    ",
                "    def __init__(self):",
                f'        super().__init__("{formatted_path}", method="{method}")',
                "    ",
                "    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:",
                '        """Validate and transform input parameters."""',
            ]

            # Add parameter validation code
            validation_code = []
            if path_params:
                validation_code.append("        # Path parameters")
                for param in path_params:
                    validation_code.extend(
                        [
                            f'        {param} = params.get("{param}")',
                            f"        if not {param}:",
                            f'            raise HTTPException(status_code=400, detail="{param.title()} is required")',
                            "",
                            "        # Format the endpoint with path parameters",
                            f"        self.endpoint = self.endpoint.format({param}={param})",
                        ]
                    )

            # Add query parameter handling for GET requests
            if method == "GET":
                query_params = [
                    p for p in endpoint.get("parameters", []) if p.get("in") == "query"
                ]
                if query_params:
                    if validation_code:
                        validation_code.append("")
                    validation_code.extend(
                        [
                            "        # Query parameters",
                            "        query_params = {}",
                        ]
                    )
                    for param in query_params:
                        param_name = param.get("name", "")
                        if not param_name:
                            continue
                        snake_case_name = self._to_snake_case(param_name)
                        validation_code.append(
                            f'        if "{snake_case_name}" in params:'
                        )
                        validation_code.append(
                            f'            query_params["{param_name}"] = params["{snake_case_name}"]'
                        )
                    validation_code.append(
                        '        return {"query_params": query_params}'
                    )
                else:
                    validation_code.append('        return {"query_params": {}}')

            # Add request body handling for non-GET requests
            elif method in ("POST", "PUT", "PATCH", "DELETE"):
                if endpoint.get("request_body"):
                    if validation_code:
                        validation_code.append("")
                    validation_code.extend(
                        [
                            "        # Request body",
                            "        body = {}",
                        ]
                    )

                    # If we have a schema, use it to generate validation code
                    content = endpoint.get("request_body", {}).get("content", {})
                    schema = None
                    for content_type in (
                        "application/json",
                        "application/x-www-form-urlencoded",
                    ):
                        if content_type in content:
                            schema = content[content_type].get("schema", {})
                            break

                    if schema and "properties" in schema:
                        for prop_name, prop_schema in schema["properties"].items():
                            snake_case_name = self._to_snake_case(prop_name)
                            required = prop_name in schema.get("required", [])

                            if required:
                                validation_code.extend(
                                    [
                                        f'        {snake_case_name} = params.get("{snake_case_name}")',
                                        f"        if not {snake_case_name}:",
                                        f'            raise HTTPException(status_code=400, detail="{prop_name} is required")',
                                        f'        body["{prop_name}"] = {snake_case_name}',
                                    ]
                                )
                            else:
                                validation_code.extend(
                                    [
                                        f'        if "{snake_case_name}" in params:',
                                        f'            body["{prop_name}"] = params["{snake_case_name}"]',
                                    ]
                                )

                    validation_code.append('        return {"body": body}')
                else:
                    validation_code.append('        return {"body": {}}')
            else:
                validation_code.append("        return {}")

            # Add indentation to validation code
            class_code.extend(validation_code)
            code.extend(class_code)

        # Add factory function
        factory_code = [
            "",
            "# Factory function to create API method instances",
            "def create_api_method(method_name: str) -> ApiMethod:",
            '    """Factory function to create API method instances based on method name."""',
            "    method_classes = {",
        ]

        for endpoint in endpoints:
            class_name = self._to_class_name(endpoint["operation_id"])
            method_name = self._to_snake_case(endpoint["operation_id"])
            factory_code.append(f'        "{method_name}": {class_name},')

        factory_code.extend(
            [
                "    }",
                "    ",
                "    method_class = method_classes.get(method_name)",
                "    if not method_class:",
                '        raise ValueError(f"Unknown method: {method_name}")',
                "    ",
                "    return method_class()",
            ]
        )

        code.extend(factory_code)

        # Join all lines with newlines
        return "\n".join(code)

    def _to_class_name(self, operation_id: str) -> str:
        """Convert an operation ID to a class name."""
        # Remove non-alphanumeric characters
        name = re.sub(r"[^a-zA-Z0-9]", " ", operation_id)

        # Convert to camel case
        return "".join(word.title() for word in name.split())

    def _to_snake_case(self, name: str) -> str:
        """Convert a camelCase or PascalCase name to snake_case."""
        # Insert underscore before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        # Insert underscore between lowercase and uppercase letters
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        # Convert to lowercase
        return s2.lower()

    def _openapi_type_to_soren_type(self, schema):
        """Map OpenAPI type/format to Soren input_type and default value."""
        t = schema.get("type", "string")
        fmt = schema.get("format", "")
        if t == "array":
            # Only support array of strings/numbers for now
            item_type = schema.get("items", {}).get("type", "string")
            if item_type in ("integer", "number"):
                return "number[]", []
            return "string[]", []
        if t in ("integer", "number"):
            return "number", schema.get("default", 0)
        if t == "boolean":
            return "boolean", schema.get("default", False)
        # Add more format-based types if needed
        return "string", schema.get("default", "")

    def _openapi_regex_for_type(self, schema):
        """Return a regex pattern for validation based on type/format."""
        t = schema.get("type", "string")
        fmt = schema.get("format", "")
        if t == "integer":
            return {"pattern": "^[0-9]+$", "message": "Must be a number"}
        if fmt == "uuid":
            return {"pattern": "^[a-fA-F0-9-]{36}$", "message": "Must be a valid UUID"}
        if fmt == "email":
            return {
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "message": "Must be a valid email address",
            }
        if fmt == "date":
            return {
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                "message": "Must be a valid date (YYYY-MM-DD)",
            }
        if fmt == "date-time":
            return {
                "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}",
                "message": "Must be a valid date-time",
            }
        return None


def generate_methods_from_openapi(
    spec_path: str, output_path: str, base_url_var: str = "BASE_URL"
):
    """Generate API method classes from an OpenAPI specification."""
    try:
        parser = OpenApiParser(spec_path)

        # Ensure output directory exists
        import os

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        result = parser.generate_api_methods(output_path, base_url_var)
        return result
    except ImportError as e:
        if "yaml" in str(e).lower():
            return "Error: PyYAML is required. Install it with: pip install pyyaml"
        return f"Import error: {str(e)}"
    except Exception as e:
        return f"Error generating API methods: {str(e)}"


def generate_method_configs(spec_path: str, output_path: str):
    """Generate method configurations for the Soren Plugins Protocol."""
    try:
        parser = OpenApiParser(spec_path)
        endpoints = parser._extract_endpoints()

        if not endpoints:
            raise ValueError("No endpoints found in the OpenAPI specification")

        # Ensure output directory exists
        import os

        os.makedirs(output_path, exist_ok=True)

        # Generate method list
        methods_list = []
        for endpoint in endpoints:
            method_name = parser._to_snake_case(endpoint["operation_id"])
            methods_list.append(
                {
                    "method": method_name,
                    "description": endpoint["description"]
                    or endpoint["summary"]
                    or f"{endpoint['method']} {endpoint['path']}",
                    "title": " ".join(word.title() for word in method_name.split("_")),
                }
            )

        # Write methods list to file
        with open(f"{output_path}/methods_list.py", "w") as f:
            f.write("methods_list = [\n")
            for method in methods_list:
                f.write("    {\n")
                f.write(f'        "method": "{method["method"]}",\n')
                # Escape quotes in description
                escaped_description = method["description"].replace('"', '\\"')
                f.write(f'        "description": "{escaped_description}",\n')
                f.write(f'        "title": "{method["title"]}",\n')
                f.write("    },\n")
            f.write("]\n")

        # Generate method configs
        methods_configs = []
        for endpoint in endpoints:
            method_name = parser._to_snake_case(endpoint["operation_id"])
            title = " ".join(word.title() for word in method_name.split("_"))

            params = []

            # Add path parameters
            path_params = re.findall(r"{([^}]+)}", endpoint["path"])
            for param_name in path_params:
                param_def = next(
                    (
                        p
                        for p in endpoint.get("parameters", [])
                        if p.get("name") == param_name and p.get("in") == "path"
                    ),
                    {},
                )
                schema = param_def.get("schema", {})
                soren_type, default_value = parser._openapi_type_to_soren_type(schema)
                regex_pattern = parser._openapi_regex_for_type(schema)
                options = None
                if "enum" in schema:
                    options = [
                        {"value": str(val), "title": str(val).title()}
                        for val in schema["enum"]
                    ]
                params.append(
                    {
                        "attr": {
                            "regex_pattern": regex_pattern
                            if regex_pattern is not None
                            else None,
                            "input_type": soren_type,
                            "secret": False,
                            "required": True,
                        },
                        "key": param_name,
                        "placeholder": f"Enter {' '.join(param_name.split('_'))}",
                        "value": default_value,
                        "title": " ".join(
                            word.title() for word in param_name.split("_")
                        ),
                        "description": param_def.get(
                            "description",
                            f"Unique identifier for the {' '.join(param_name.split('_'))}",
                        ),
                        **({"options": options} if options else {}),
                    }
                )

            # Add query parameters for GET requests
            if endpoint["method"] == "GET":
                query_params = [
                    p for p in endpoint.get("parameters", []) if p.get("in") == "query"
                ]
                for param in query_params:
                    param_name = param.get("name", "")
                    if not param_name:
                        continue
                    required = param.get("required", False)
                    schema = param.get("schema", {})
                    soren_type, default_value = parser._openapi_type_to_soren_type(
                        schema
                    )
                    regex_pattern = parser._openapi_regex_for_type(schema)
                    options = None
                    if "enum" in schema:
                        options = [
                            {"value": str(val), "title": str(val).title()}
                            for val in schema["enum"]
                        ]
                    param_config = {
                        "attr": {
                            "regex_pattern": regex_pattern
                            if regex_pattern is not None
                            else None,
                            "input_type": soren_type,
                            "secret": False,
                            "required": required,
                        },
                        "key": param_name,
                        "placeholder": f"Enter {' '.join(param_name.split('_'))}",
                        "value": default_value,
                        "title": " ".join(
                            word.title() for word in param_name.split("_")
                        ),
                        "description": param.get(
                            "description", f"Parameter: {param_name}"
                        ),
                        **({"options": options} if options else {}),
                    }
                    params.append(param_config)

            # Add request body parameters for non-GET requests
            elif endpoint["method"] in ("POST", "PUT", "PATCH", "DELETE"):
                if endpoint.get("request_body"):
                    content = endpoint.get("request_body", {}).get("content", {})
                    schema = None
                    for content_type in (
                        "application/json",
                        "application/x-www-form-urlencoded",
                    ):
                        if content_type in content:
                            schema = content[content_type].get("schema", {})
                            break
                    if schema and "properties" in schema:
                        for prop_name, prop_schema in schema["properties"].items():
                            required = prop_name in schema.get("required", [])
                            soren_type, default_value = (
                                parser._openapi_type_to_soren_type(prop_schema)
                            )
                            regex_pattern = parser._openapi_regex_for_type(prop_schema)
                            options = None
                            if "enum" in prop_schema:
                                options = [
                                    {"value": str(val), "title": str(val).title()}
                                    for val in prop_schema["enum"]
                                ]
                            param_config = {
                                "attr": {
                                    "regex_pattern": regex_pattern
                                    if regex_pattern is not None
                                    else None,
                                    "input_type": soren_type,
                                    "secret": prop_schema.get("format") == "password",
                                    "required": required,
                                },
                                "key": prop_name,
                                "placeholder": f"Enter {' '.join(prop_name.split('_'))}",
                                "value": default_value,
                                "title": " ".join(
                                    word.title() for word in prop_name.split("_")
                                ),
                                "description": prop_schema.get(
                                    "description", f"Parameter: {prop_name}"
                                ),
                                **({"options": options} if options else {}),
                            }
                            params.append(param_config)

            # If no parameters were found, add an empty parameter
            if not params:
                params = [{}]

            methods_configs.append(
                {
                    "name": method_name,
                    "title": title,
                    "description": endpoint["description"]
                    or endpoint["summary"]
                    or f"{endpoint['method']} {endpoint['path']}",
                    "params": params,
                }
            )

        # Write methods configs to file
        with open(f"{output_path}/methods_configs.py", "w") as f:
            f.write("methods_configs = [\n")
            for config in methods_configs:
                f.write("    {\n")
                f.write(f'        "name": "{config["name"]}",\n')
                f.write(f'        "title": "{config["title"]}",\n')
                # Escape quotes in description
                escaped_description = config["description"].replace('"', '\\"')
                f.write(f'        "description": "{escaped_description}",\n')
                f.write('        "params": [\n')

                for param in config["params"]:
                    if not param:  # Empty parameter
                        f.write("            {},\n")
                        continue

                    f.write("            {\n")
                    f.write('                "attr": {\n')
                    f.write(
                        f'                    "regex_pattern": {param["attr"]["regex_pattern"]},\n'
                    )
                    f.write(
                        f'                    "input_type": "{param["attr"]["input_type"]}",\n'
                    )
                    f.write(
                        f'                    "secret": {str(param["attr"]["secret"]).lower()},\n'
                    )
                    f.write(
                        f'                    "required": {str(param["attr"]["required"]).lower()},\n'
                    )
                    f.write("                },\n")
                    f.write(f'                "key": "{param["key"]}",\n')
                    f.write(
                        f'                "placeholder": "{param["placeholder"]}",\n'
                    )
                    f.write(f'                "value": {param["value"]},\n')
                    f.write(f'                "title": "{param["title"]}",\n')
                    # Escape quotes in description
                    escaped_param_description = param["description"].replace('"', '\\"')
                    f.write(
                        f'                "description": "{escaped_param_description}",\n'
                    )

                    # Add options if present
                    if "options" in param:
                        f.write('                "options": [\n')
                        for option in param["options"]:
                            f.write(
                                f'                    {{"value": "{option["value"]}", "title": "{option["title"]}"}},\n'
                            )
                        f.write("                ],\n")

                    f.write("            }},\n")

                f.write("        ],\n")
                f.write("    }},\n")
            f.write("]\n")

        return (
            f"Generated {len(methods_configs)} method configurations in {output_path}"
        )
    except Exception as e:
        return f"Error generating method configurations: {str(e)}"
