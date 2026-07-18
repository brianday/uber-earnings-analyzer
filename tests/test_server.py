"""Integration tests for the MCP server."""

import pytest
from mcp.shared.memory import (
    create_connected_server_and_client_session,
)

from uber_earnings_analyzer.server import mcp


@pytest.mark.anyio
async def test_server_exposes_expected_tools() -> None:
    """An MCP client should discover both earnings tools."""
    async with create_connected_server_and_client_session(
        mcp,
    ) as client_session:
        result = await client_session.list_tools()

    tool_names = {tool.name for tool in result.tools}

    assert tool_names == {
        "get_earnings_by_day",
        "get_earnings_by_hour",
    }


@pytest.mark.anyio
async def test_daily_earnings_tool_returns_results() -> None:
    """The daily tool should return data through MCP."""
    async with create_connected_server_and_client_session(
        mcp,
    ) as client_session:
        result = await client_session.call_tool(
            "get_earnings_by_day",
            arguments={},
        )

    assert result.isError is False
    assert result.structuredContent is not None

    daily_results = result.structuredContent["result"]

    assert daily_results[0]["date"] == "2026-07-15"
    assert daily_results[0]["total_earnings"] == 41.20
    assert daily_results[0]["trip_count"] == 2