from src.plugin_sdk.method import ApiEndpoint, MethodMetadata, PluginMethod

list_projects = PluginMethod(
    metadata=MethodMetadata(
        name="gitlab_list_projects",
        title="List GitLab Projects",
        description="List projects the authenticated user has access to",
        parameters=[],
    ),
    endpoint=ApiEndpoint(
        provider="gitlab",
        url="/projects?membership=true",
        method="GET",
        headers={"Accept": "application/json"},
    ),
)
