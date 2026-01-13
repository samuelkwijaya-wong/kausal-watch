from __future__ import annotations

from typing import TYPE_CHECKING

from fastmcp.exceptions import ToolError

from mcp_server.__generated__.schema import MCPUserDetails, MCPUserDetailsMe

from .helpers import execute_operation

if TYPE_CHECKING:
    from fastmcp import FastMCP


async def user_details() -> MCPUserDetailsMe:
    """
    Get details about the currently authenticated user.

    Returns the user's ID, email, name, and superuser status.
    """
    result = await execute_operation(MCPUserDetails, MCPUserDetails.Arguments())  # type: ignore[type-var]

    if result.me is None:
        raise ToolError("Not authenticated or user not found")

    return result.me


def register_user_tools(mcp: FastMCP) -> None:
    """Register all user-related MCP tools."""

    mcp.tool(user_details)
