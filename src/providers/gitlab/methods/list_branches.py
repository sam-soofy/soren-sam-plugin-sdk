from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

list_branches = PluginMethod(
    metadata=MethodMetadata(
        name="gitlab_list_branches",
        title="List GitLab Branches",
        description="List branches of a GitLab project",
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
        url="/projects/{project_id}/repository/branches",
        method="GET",
        headers={"Accept": "application/json"},
    ),
)
