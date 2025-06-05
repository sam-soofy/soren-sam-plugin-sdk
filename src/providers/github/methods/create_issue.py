from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

create_issue = PluginMethod(
    metadata=MethodMetadata(
        name="github_create_issue",
        title="Create GitHub Issue",
        description="Create an issue in a GitHub repository",
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
            ParameterDefinition(
                name="title", type="string", required=True, description="Issue title"
            ),
            ParameterDefinition(
                name="body", type="string", required=False, description="Issue body"
            ),
        ],
    ),
    endpoint=ApiEndpoint(
        provider="github",
        url="/repos/{owner}/{repo}/issues",
        method="POST",
        headers={"Accept": "application/vnd.github.v3+json"},
        body_mapping={"title": "title", "body": "body"},
    ),
)
