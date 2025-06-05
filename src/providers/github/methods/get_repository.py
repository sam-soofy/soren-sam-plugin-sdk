from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

get_repository = PluginMethod(
    metadata=MethodMetadata(
        name="github_get_repository",
        title="Get GitHub Repository",
        description="Get details of a GitHub repository",
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
        url="/repos/{owner}/{repo}",
        method="GET",
        headers={"Accept": "application/vnd.github.v3+json"},
    ),
)
