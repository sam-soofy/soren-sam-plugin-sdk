from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

list_branches = PluginMethod(
    metadata=MethodMetadata(
        name="github_list_branches",
        title="List GitHub Branches",
        description="List branches of a GitHub repository",
        parameters=[
            ParameterDefinition(
                name="owner",
                type="string",
                required=True,
                description="Owner of the repository",
            ),
            ParameterDefinition(
                name="repo", type="string", required=True, description="Repository name"
            ),
        ],
    ),
    endpoint=ApiEndpoint(
        provider="github",
        url="/repos/{owner}/{repo}/branches",
        method="GET",
        headers={"Accept": "application/vnd.github.v3+json"},
    ),
)
