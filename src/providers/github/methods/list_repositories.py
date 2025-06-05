from src.plugin_sdk.method import ApiEndpoint, MethodMetadata, PluginMethod

list_repositories = PluginMethod(
    metadata=MethodMetadata(
        name="github_list_repositories",
        title="List GitHub Repositories",
        description="List repositories for the authenticated user",
        parameters=[],
    ),
    endpoint=ApiEndpoint(
        provider="github",
        url="/user/repos",
        method="GET",
        headers={"Accept": "application/vnd.github.v3+json"},
    ),
)
