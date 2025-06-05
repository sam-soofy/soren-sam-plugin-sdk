from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

get_project = PluginMethod(
    metadata=MethodMetadata(
        name="gitlab_get_project",
        title="Get GitLab Project",
        description="Get details of a GitLab project",
        parameters=[
            ParameterDefinition(
                name="project_id",
                type="number",
                required=True,
                description="ID of the project",
            ),
        ],
    ),
    endpoint=ApiEndpoint(
        provider="gitlab",
        url="/projects/{project_id}",
        method="GET",
        headers={"Accept": "application/json"},
    ),
)
