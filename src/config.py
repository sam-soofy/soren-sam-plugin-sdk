"""
This config constant dictionary  contains the base URL for the different API services.
"""

BASE_URLS = {
    "github": "https://api.github.com",
    "gitlab": "https://gitlab.com/api/v4",
    # future providers here…
}


"""
The `plugin_config` dictionary defines the configuration for a plugin named "codebashing-plugin". It includes the following settings:

- `name`: The name of the plugin, "example-plugin".
- `author`: The author of the plugin, "Sam Soofy".
- `version`: The version of the plugin, "v1.0.1".
- `proto`: The protocol version, "v0.0.1".
- `schema_version`: The schema version, "srn-schema-v1".
- `init_config`: A list of configuration parameters, including:
    - `name`: The name of the configuration, "global_configs".
    - `title`: The title of the configuration, "Example settings".
    - `description`: The description of the configuration, "Required parameters".
    - `params`: A list of configuration parameters, including:
        - `token`: The API token required to use the Example service. This is a required string parameter.
        - `x_api_key`: The X-API-Key required to use the CodeBashing service. This is a required string parameter.
"""

plugin_config = {
    "name": "SCM Provider",
    "author": "Sam Soofy",
    "version": "v1.0.0",
    "proto": "v0.1.0",
    "schema_version": "srn-schema-v1",
    "init_config": [
        {
            "name": "global_configs",
            "title": "SCM Provider Settings",
            "description": "Required parameters for SCM providers (GitHub & GitLab)",
            "params": [
                {
                    "attr": {"input_type": "string", "secret": True, "required": True},
                    "key": "github_token",
                    "title": "GitHub Personal Access Token",
                    "description": "Personal access token for GitHub API",
                    "placeholder": "e.g. ghp_XXXXXXXXXXXXXXXXXXXXXX",
                    "value": [],
                },
                {
                    "attr": {"input_type": "string", "secret": True, "required": True},
                    "key": "gitlab_token",
                    "title": "GitLab Personal Access Token",
                    "description": "Personal access token for GitLab API",
                    "placeholder": "e.g. glpat-XXXXXXXXXXXXXXXX",
                    "value": [],
                },
            ],
        }
    ],
}
