from src.plugin_sdk.method import (
    ApiEndpoint,
    MethodMetadata,
    ParameterDefinition,
    PluginMethod,
)

list_issues = PluginMethod(
    metadata=MethodMetadata(
        name="github_list_issues",
        title="List GitHub Issues",
        description="List issues in a GitHub repository",
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
                name="state",
                type="string",
                required=False,
                description="Issue state (open, closed, all)",
                default="open",
            ),
        ],
    ),
    endpoint=ApiEndpoint(
        provider="github",
        url="/repos/{owner}/{repo}/issues",
        method="GET",
        headers={"Accept": "application/vnd.github.v3+json"},
        query_param_mapping={"state": "state"},
    ),
)
