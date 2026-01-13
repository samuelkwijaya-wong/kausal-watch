from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastmcp.exceptions import ToolError

from mcp_server.__generated__.schema import MCPGetAction, MCPGetActionAction, MCPListActions, MCPListActionsPlanactions

from .helpers import execute_operation

if TYPE_CHECKING:
    from fastmcp import FastMCP


async def list_actions(
    plan: Annotated[str, "The plan identifier (e.g., 'sunnydale', 'tampere-ilmasto')"],
    category: Annotated[str | None, 'Filter by category ID (includes descendants)'] = None,
    first: Annotated[int | None, 'Limit number of results (default: all)'] = None,
    order_by: Annotated[str | None, "Order by field: 'updated_at' or 'identifier'"] = None,
) -> list[MCPListActionsPlanactions]:
    """
    List actions from a climate action plan with optional filtering.

    Returns actions with their status, responsible organizations, and categories.
    Use the category filter to narrow down to a specific theme or strategy.
    """
    result = await execute_operation(
        MCPListActions, # type: ignore[type-var]
        MCPListActions.Arguments(plan=plan, category=category, first=first, orderBy=order_by),
    )

    if result.plan_actions is None:
        raise ToolError(f"Plan '{plan}' not found or not accessible")

    return result.plan_actions


async def get_action(
    plan: Annotated[str, "The plan identifier (e.g., 'sunnydale', 'tampere-ilmasto')"],
    identifier: Annotated[str, "The action identifier within the plan (e.g., '1.1.1', 'A.2')"],
) -> MCPGetActionAction:
    """
    Get detailed information about a specific action in a climate action plan.

    Returns comprehensive action details including:
    - Status and completion information
    - Responsible organizations and contact persons
    - Tasks and their states
    - Related indicators with latest values
    - Links and status updates
    - Related and dependent actions
    """
    result = await execute_operation(MCPGetAction, MCPGetAction.Arguments(plan=plan, identifier=identifier))  # type: ignore[type-var]

    if result.action is None:
        raise ToolError(f"Action '{identifier}' not found in plan '{plan}'")

    return result.action


def register_action_tools(mcp: FastMCP) -> None:
    """Register all action-related MCP tools."""

    mcp.tool(list_actions)
    mcp.tool(get_action)
