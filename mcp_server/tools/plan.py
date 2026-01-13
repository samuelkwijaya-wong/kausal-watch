from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastmcp.exceptions import ToolError

from mcp_server.__generated__.schema import MCPGetPlan, MCPListPlans

from .helpers import execute_operation

if TYPE_CHECKING:
    from fastmcp import FastMCP


async def list_plans() -> MCPListPlans:
    """List accessible plans. Returns plans where the user has a staff role."""


    result = await execute_operation(MCPListPlans, MCPListPlans.Arguments())  # type: ignore[type-var]
    if result.plans is None:
        raise ToolError("No plans found")
    return result


async def get_plan(
    identifier: Annotated[str, "The unique identifier of the plan (e.g., 'sunnydale', 'tampere-ilmasto')"],
) -> MCPGetPlan:
    """Get detailed information about a specific action plan."""
    result = await execute_operation(MCPGetPlan, MCPGetPlan.Arguments(identifier=identifier))  # type: ignore[type-var]

    if result.plan is None:
        raise ToolError(f"Plan '{identifier}' not found")

    return result


def register_plan_tools(mcp: FastMCP) -> None:
    """Register all plan-related MCP tools."""

    mcp.tool(list_plans)
    mcp.tool(get_plan)
