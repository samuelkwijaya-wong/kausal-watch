# MCP Server Architecture

## Overview

Kausal Watch exposes an MCP (Model Context Protocol) server at `/mcp` to enable AI assistants (LibreChat, Claude.ai, etc.) to query climate action plan data.

## Architecture

- **Framework**: FastMCP with Streamable HTTP transport
- **Mounting**: Under `/mcp` in the Django ASGI app via `ProtocolTypeRouter`
- **Authentication**: OAuth2 Bearer tokens via existing `HTTPMiddleware`
- **Data Layer**: GraphQL queries executed programmatically, reusing all existing permission logic

## File Structure

```
mcp_server/
├── __init__.py              # Package init
├── server.py                # FastMCP app, core utilities, and tool registration
├── queries.graphql          # GraphQL queries for MCP tools
├── mcp_client_tool.py       # CLI tool for testing
├── tools/                   # Tool implementations by domain
│   ├── __init__.py          # Exports register functions
│   ├── helpers.py           # Shared utilities (execute_operation)
│   ├── plan.py              # Plan-related tools (list_plans, get_plan)
│   ├── action.py            # Action-related tools (list_actions, get_action)
│   └── user.py              # User-related tools (user_details)
└── __generated__/           # Auto-generated GraphQL client code (DO NOT EDIT)
    └── schema.py            # Pydantic models for all operations
```

## Development Workflow

### Adding a New Tool

1. **Add the GraphQL query** to `mcp_server/queries.graphql`:

   ```graphql
   query MCPGetPlan($identifier: ID!) @context(input: {identifier: $identifier}) {
       plan(id: $identifier) {
           id
           identifier
           name
           shortName
           # ... other fields
       }
   }
   ```

   > **Note**: Use the `@context` directive on plan-specific queries to activate the
   > correct language and plan context. Pass the plan identifier via
   > `@context(input: {identifier: $planVariable})`.

2. **Regenerate the client code**:

   ```bash
   python manage.py export_schema aplans.schema > schema.graphql
   uvx turms gen
   ```

   This generates typed Pydantic models in `mcp_server/__generated__/schema.py`.

3. **Add the tool** to the appropriate file in `mcp_server/tools/`:

   ```python
   # In mcp_server/tools/plan.py
   from mcp_server.__generated__.schema import MCPGetPlan

   from .helpers import execute_operation

   async def get_plan(identifier: str) -> MCPGetPlan:
       """Get plan details by identifier."""
       result = await execute_operation(MCPGetPlan, MCPGetPlan.Arguments(identifier=identifier))
       if result.plan is None:
           raise ToolError(f"Plan '{identifier}' not found")
       return result
   ```

   Tools are organized by domain (e.g., `plan.py`, `action.py`, `indicator.py`).
   Each module exports a `register_*_tools(mcp)` function called from `server.py`.
   The tool schema is introspected through the function type annotations,
   so the types need to be available in runtime (not imported in a TYPE_CHECKING block).

## Testing

### Using the CLI Tool

The `mcp_client_tool.py` script provides a simple way to test the MCP server:

```bash
# List available tools
uv run mcp_server/mcp_client_tool.py --list-tools

# Call a tool
uv run mcp_server/mcp_client_tool.py --call list_plans

# Call with arguments
uv run mcp_server/mcp_client_tool.py --call hello_world --args '{"name": "World"}'

# Get raw JSON output
uv run mcp_server/mcp_client_tool.py --call list_plans --raw
```

**Prerequisites**: Set `MCP_CLIENT_TOKEN` in your `.env` file with a valid OAuth2 access token.

### Using MCP Inspector

1. Start the server: `uvicorn aplans.asgi:application --reload`
2. Open MCP Inspector and connect to `http://localhost:8000/mcp`
3. Add authorization header: `Authorization: Bearer <your-token>`

## Authentication Flow

1. Client sends `Authorization: Bearer <token>` header
2. `HTTPMiddleware` validates the token and sets `scope['user']`
3. `WatchGraphQLContext` reads the user from the ASGI scope
4. GraphQL resolvers use `info.context.user` for permission checks

## v0 Tools (Read-Only)

| Tool | Description | Status |
|------|-------------|--------|
| `list_plans` | List accessible plans | Implemented |
| `get_plan` | Get plan details | Implemented |
| `list_actions` | List/filter actions | Implemented |
| `get_action` | Get action details | Implemented |
| `user_details` | Get current user info | Implemented |
| `search` | Full-text search | Planned |
| `list_indicators` | List indicators | Planned |
| `get_indicator` | Get indicator with values | Planned |
| `get_category_tree` | Hierarchical categories | Planned |
| `list_organizations` | Organizations in plan | Planned |
| `get_action_status_summary` | Dashboard stats | Planned |

## Future Considerations

- Write tools (update action status, add comments)
- Customer-facing deployment with plan-scoped tokens
- MCP Resources for plans/actions
- MCP Prompts for common queries
- Generalize to `kausal_common` for Kausal Paths reuse
