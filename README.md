A pythonic SDK to help generating and accelerating plugin developments with multiple templates in mind, shipped with sdk to use. 

# Soren SCM Source Control Management Provider (Plugin) [Example Template]

This project is a **Soren Plugin** (also called Tool on Marketplace) for integrating Source Control Management (SCM) systems with the Soren platform. It serves as an **example/template** plugin with multiple **providers**, originally based on a plugin integration, and is intended to be adapted for SCM plugin development in future steps. It exposes a set of methods (actions) via REST APIs, enabling workflow automation and integration with external services. **(We use the Tool & Plugin interchangeably)**

---

## What is a Soren Plugin (Tool)?

A **Soren Plugin** is a modular tool that implements the [Soren Plugins Protocol](#soren-plugins-protocol) to expose a set of methods (API actions) through a standardized REST interface. Plugins are designed to be:
- **Provider**: Easily add, organize and use multiple service provider (optional)
- **Extensible**: Easily add new methods for new APIs or workflows.
- **Auto-discoverable**: Methods are registered automatically.
- **Reusable**: Common SDK patterns and utilities for all providers.

### Soren Plugins Protocol
- Each plugin/provider exposes methods as REST endpoints.
- Methods are described with metadata and parameter schemas.
- The platform auto-discovers and registers all available methods.

## What is a Provider in Plugin?

A **provider** is simply a service provider that usually plugins may interact with to provide functionalites, as a pluged-in tool into Soren workflow. The provider term and some configs may be optional and skipped if only one provider is necessary in a specific plugin.

---

## Plugin SDK Architecture

The Plugin SDK offers a blueprint for building new plugins with multiple providers:

### Directory Structure

```text
src/
├── api/                # API routes and legacy support (minimal)
├── plugin_sdk/         # SDK: base classes, registry, controller
├── providers/
│   └── <provider_name>/
│       ├── __init__.py
│       └── methods/
│           ├── __init__.py
│           ├── method_one.py
│           └── method_two.py
└── config.py           # Global provider configuration
```

- **`providers/<provider_name>/methods/`**: Each `.py` file defines a `PluginMethod` instance.
- **`config.py`**: Global configuration for the provider (see below).

### Key SDK Components
- `PluginMethod`: Base class for defining a method (see `plugin_sdk/method.py`).
- `PluginRegistry`: Auto-discovers and registers all methods.
- `PluginController`: Executes methods via the REST API.

---

## How to Create a Provider

1. **Create a new provider directory:**
   - `src/providers/<provider_name>/`
   - Add a `methods/` subdirectory.

2. **Define methods:**
   - Each method is a `PluginMethod` instance in its own file under `methods/`.
   - Example:

```python
from src.plugin_sdk.method import PluginMethod, MethodMetadata, ApiEndpoint, ParameterDefinition

list_items = PluginMethod(
    metadata=MethodMetadata(
        name="<provider>_list_items",
        title="List Items",
        description="Retrieve items from <Provider>",
        parameters=[
            ParameterDefinition(name="filter", type="string", required=False, description="Filter query"),
        ],
    ),
    endpoint=ApiEndpoint(
        url="https://api.example.com/v1/items",
        method="GET",
        headers={"Content-Type": "application/json"},
        query_param_mapping={"filter": "q"},
    ),
)
```

3. **Export methods in `__init__.py`:**

```python
from .methods.list_items import list_items
__all__ = ["list_items"]
```

4. **Auto-discovery:**
   - The registry will automatically find and register all `PluginMethod` instances in `src.providers`.

---

## Auto-Discovery

The `PluginRegistry` supports recursive discovery of all `PluginMethod` instances:

```python
from src.plugin_sdk.registry import PluginRegistry
registry = PluginRegistry()
registry.auto_discover("src.providers")
```

---

## REST API Endpoints

The plugin exposes the following endpoints (by default, **on port 80**):

- `GET    /api/methods` — List all registered methods
- `GET    /api/method/{method_name}` — Get configuration for a method
- `POST   /api/method/{method_name}` — Execute a method with parameters
- `GET    /api/version` — Get provider version/config
- `POST   /api/version` — Update provider config

**Note:** The default port is now **80** (not 8000).

---

## OpenAPI Method Generator

You can scaffold methods and configs from an OpenAPI spec:

```python
from src.api.core.api_method_generator import generate_methods_from_openapi, generate_method_configs

generate_methods_from_openapi(
    spec_path="path/to/openapi.json",
    output_path="src/providers/<provider_name>/methods/generated.py",
    base_url_var="BASE_URL"
)
generate_method_configs(
    spec_path="path/to/openapi.json",
    output_path="src/api/core"
)
```

---

## OpenAPI Method Generator: Documentation & Usage

The OpenAPI Method Generator helps you quickly scaffold Soren-compatible provider methods and configuration files from any OpenAPI specification (JSON or YAML).

### What It Does
- **Generates Python method classes** for each endpoint in the OpenAPI spec, ready to use in your provider's `methods/` directory.
- **Generates Soren method configuration files** (`methods_list.py` and `methods_configs.py`) for use by the Soren Plugins Protocol and UI.
- Handles parameter types, defaults, enums/options, validation regex, and descriptions according to the Soren protocol.

### Prerequisites
- Your OpenAPI spec must be in JSON or YAML format.
- If using YAML, ensure you have `PyYAML` installed: `pip install pyyaml`

### How to Use

1. **Generate Python Method Classes**
   - This will create a Python file with all API method classes for your provider:
   
   ```python
   from src.api.core.api_method_generator import generate_methods_from_openapi
   
   generate_methods_from_openapi(
       spec_path="path/to/openapi.json",  # or .yaml
       output_path="src/providers/<provider_name>/methods/generated.py",
       base_url_var="BASE_URL"  # or your base URL variable
   )
   ```

2. **Generate Soren Method Configs**
   - This will create `methods_list.py` and `methods_configs.py` in the specified output directory:
   
   ```python
   from src.api.core.api_method_generator import generate_method_configs
   
   generate_method_configs(
       spec_path="path/to/openapi.json",  # or .yaml
       output_path="src/api/core"
   )
   ```

### Output
- **Python method classes:** Place the generated file in your provider's `methods/` directory and import the methods in your provider's `__init__.py`.
- **Soren config files:** Place the generated `methods_list.py` and `methods_configs.py` in your API core/config directory.

### Notes
- The generator will infer parameter types, defaults, and validation rules from the OpenAPI schema.
- Enum values in the OpenAPI spec will be converted to Soren-compatible options.
- Regex validation is added for common types (integer, uuid, email, date, etc.).
- You can further customize the generated files as needed for your provider.

---

## Example: Adding a Method

1. Create a new file in `src/providers/<provider_name>/methods/` (e.g., `list_users.py`).
2. Define your method as a `PluginMethod` instance (see above).
3. Import it in your provider's `__init__.py` and add to `__all__`.

---

## Configuration

Global plugin configuration is defined in `src/config.py` under the `plugin_config` dictionary. You must keep the top-level protocol keys intact; you may only add or update entries in the `init_config` list.

### Multi-provider credentials
In the default template we define two tokens in the `global_configs` section for GitHub and GitLab:

```python
plugin_config = {
    "name": "SCM Provider",
    "author": "Sam Soofy",
    "version": "v1.0.1",
    "proto": "v0.1.0",
    "schema_version": "srn-schema-v1",
    "init_config": [
        {
            "name": "global_configs",
            "title": "SCM Provider Settings",
            "description": "Credentials for SCM providers",
            "params": [
                {
                    "key": "github_token",
                    "title": "GitHub Personal Access Token",
                    "description": "Your GitHub PAT",
                    "placeholder": "ghp_…",
                    "attr": {
                        "input_type": "string",
                        "secret": true,
                        "required": true
                    },
                    "value": []
                },
                {
                    "key": "gitlab_token",
                    "title": "GitLab Personal Access Token",
                    "description": "Your GitLab PAT",
                    "placeholder": "glpat-…",
                    "attr": {
                        "input_type": "string",
                        "secret": true,
                        "required": true
                    },
                    "value": []
                }
            ]
        }
    ]
}
```

When methods execute, the SDK picks which token to send based on the request URL:
- If the URL contains `gitlab.com` or `/api/v4`, the GitLab token is used.
- Otherwise, the GitHub token is used.

If you only supply one of these tokens, that credential will be applied to all calls—so single-provider plugins continue working unchanged.

### Optional BASE_URLS map
To keep method definitions cleaner, you may declare a `BASE_URLS` map in `src/config.py`:

```python
BASE_URLS = {
    "github": "https://api.github.com",
    "gitlab": "https://gitlab.com/api/v4",
}
```
Endpoints defined as paths (e.g. `"/user/repos"`) will have the correct base URL prepended automatically.

---

## Dependencies

- FastAPI: Web framework for building APIs
- httpx: Async HTTP client
- Pydantic: Data validation and settings management
- PyYAML: YAML parser for OpenAPI specifications (optional)

---

## Containerization & Deployment

### Build & Deploy

**Versioning Convention:**  
The Docker image tag uses the format `<protocol-version>-<plugin-version>`, where:
- The first part (`0.1`) refers to the Soren Plugin Protocol version.
- The second part (`1.0.1`) refers to the plugin's own version.

**Example:**

```sh
# Build the Docker image
$ docker build -t YOUR_ACCOUNT_REPO/example-plugin:0.1-1.0.1-slim .

# Login to Docker Hub
$ docker login

# Push the image
$ docker push YOUR_ACCOUNT_REPO/example-plugin:0.1-1.0.1-slim
```

### Local Development

```sh
# Run locally (detached)
$ docker compose -f docker-compose.yml  down --remove-orphans && clear && docker compose -f docker-compose.yml up 
```

---

## Migration Note

The previous service/controller/config pattern under `src/api/` is now deprecated. All new development should use the Provider SDK pattern described above.
