from __future__ import annotations

from fastmcp import FastMCP

from kausal_common.deployment import get_deployment_build_id

from .tools import register_action_tools, register_plan_tools, register_user_tools

# Create FastMCP without built-in auth - we handle auth ourselves via MCPAuthMiddleware
mcp = FastMCP(
    name="KausalWatch",
    instructions="""
        Provides tools for accessing and modifying action plans, indicators, and other
        related objects on the Kausal Watch platform.
    """,
    version=get_deployment_build_id() or "0.1.0-dev",
)

# Register tools from separate modules
register_plan_tools(mcp)
register_action_tools(mcp)
register_user_tools(mcp)
