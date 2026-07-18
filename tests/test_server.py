"""Integration tests for the MCP server."""

import pytest
from mcp.shared.memory import (
    create_connected_server_and_client_session,
)

from uber_earnings_analyzer.server import mcp

@pytest.fixture(autouse=True)
def use_sample_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure MCP tests use the deterministic public sample dataset."""
    monkeypatch.delenv("UBER_EARNINGS_CSV", raising=False)


@pytest.mark.anyio
async def test_server_exposes_expected_tools() -> None:
    """An MCP client should discover all earnings tools."""
    async with create_connected_server_and_client_session(
        mcp,
    ) as client_session:
        result = await client_session.list_tools()

    tool_names = {tool.name for tool in result.tools}

    assert tool_names == {
        "compare_weeks",
        "get_earnings_by_day",
        "get_earnings_by_hour",
        "get_weekly_earnings_trend",
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


@pytest.mark.anyio
async def test_compare_weeks_tool_returns_results() -> None:
    """The weekly comparison should be available through MCP."""
    async with create_connected_server_and_client_session(
        mcp,
    ) as client_session:
        result = await client_session.call_tool(
            "compare_weeks",
            arguments={},
        )

    assert result.isError is False
    assert result.structuredContent is not None

    comparison = result.structuredContent

    assert comparison["current_week"]["total_earnings"] == 172.07
    assert comparison["previous_week"]["total_earnings"] == 145.00
    assert comparison["earnings_change"] == 27.07
    assert comparison["percentage_change"] == 18.67

@pytest.mark.anyio
async def test_weekly_trend_tool_accepts_week_count() -> None:
    """The trend tool should accept an MCP input argument."""
    async with create_connected_server_and_client_session(
        mcp,
    ) as client_session:
        result = await client_session.call_tool(
            "get_weekly_earnings_trend",
            arguments={"weeks": 2},
        )

    assert result.isError is False
    assert result.structuredContent is not None

    trend = result.structuredContent["result"]

    assert len(trend) == 2
    assert trend[0]["start_date"] == "2026-07-06"
    assert trend[0]["total_earnings"] == 145.00
    assert trend[1]["start_date"] == "2026-07-13"
    assert trend[1]["total_earnings"] == 172.07
    assert trend[1]["percentage_change"] == 18.67