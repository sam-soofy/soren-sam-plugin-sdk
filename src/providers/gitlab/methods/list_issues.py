from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

list_issues = PluginMethod(
    metadata=MethodMetadata(
        name="gitlab_list_issues",
        title="List GitLab Issues",
        description="List issues in a GitLab project",
        parameters=[
            ParameterDefinition(
                name="project_id",
                type="number",
                required=True,
                description="ID of the project",
            ),
            ParameterDefinition(
                name="state",
                type="string",
                required=False,
                description="Issue state (opened, closed, all)",
                default="opened",
            ),
        ],
    ),
    endpoint=ApiEndpoint(
        provider="gitlab",
        url="/projects/{project_id}/issues",
        method="GET",
        headers={"Accept": "application/json"},
        query_param_mapping={"state": "state"},
    ),
)
