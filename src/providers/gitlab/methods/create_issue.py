from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

create_issue = PluginMethod(
    metadata=MethodMetadata(
        name="gitlab_create_issue",
        title="Create GitLab Issue",
        description="Create an issue in a GitLab project",
        parameters=[
            ParameterDefinition(
                name="project_id",
                type="number",
                required=True,
                description="ID of the project",
            ),
            ParameterDefinition(
                name="title", type="string", required=True, description="Issue title"
            ),
            ParameterDefinition(
                name="description",
                type="string",
                required=False,
                description="Issue description",
            ),
        ],
    ),
    endpoint=ApiEndpoint(
        provider="gitlab",
        url="/projects/{project_id}/issues",
        method="POST",
        headers={"Accept": "application/json"},
        body_mapping={"title": "title", "description": "description"},
    ),
)
