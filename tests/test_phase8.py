"""Unit and headless tests for Godot Phase 8 tools (Autoloads, Signals & Event Wiring, Expression Evaluation)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.autoload import (
    GetAutoloadsInput,
    SetAutoloadInput,
)
from godot_mcp.models.runtime_eval import EvaluateExpressionInput
from godot_mcp.models.signal_wire import (
    ConnectSignalInput,
    GetNodeSignalsInput,
    GetSignalConnectionsInput,
)
from godot_mcp.tools.autoload_tools import (
    handle_get_autoloads,
    handle_set_autoload,
)
from godot_mcp.tools.eval_tools import handle_evaluate_expression
from godot_mcp.tools.signal_tools import (
    handle_connect_signal,
    handle_get_node_signals,
    handle_get_signal_connections,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase8_tools_mock() -> None:
    """Test Phase 8 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Get Autoloads
    auto_res = await handle_get_autoloads(client, GetAutoloadsInput())
    assert "Autoload Singletons" in auto_res
    assert "GameManager" in auto_res

    # 2. Set Autoload
    set_res = await handle_set_autoload(
        client,
        SetAutoloadInput(
            name="EventBus",
            path="res://scripts/event_bus.gd",
            is_singleton=True,
        ),
    )
    assert "EventBus" in set_res

    # 3. Get Node Signals
    sig_res = await handle_get_node_signals(
        client,
        GetNodeSignalsInput(node_path="/root/Main/Button"),
    )
    assert "Signals on `Button`" in sig_res
    assert "pressed" in sig_res

    # 4. Connect Signal
    conn_res = await handle_connect_signal(
        client,
        ConnectSignalInput(
            source_node_path="/root/Main/Button",
            signal_name="pressed",
            target_node_path="/root/Main/GameManager",
            method_name="_on_button_pressed",
            persist=True,
        ),
    )
    assert "Signal Connected" in conn_res
    assert "_on_button_pressed" in conn_res

    # 5. Get Signal Connections
    graph_res = await handle_get_signal_connections(
        client,
        GetSignalConnectionsInput(node_path="/root/Main/Button"),
    )
    assert "Signal Connection Graph" in graph_res
    assert "outgoing" in graph_res.lower()

    # 6. Evaluate Expression
    eval_res = await handle_evaluate_expression(
        client,
        EvaluateExpressionInput(
            expression="2 * PI * radius",
            input_variables={"radius": 5.0},
        ),
    )
    assert "Expression Evaluation" in eval_res
    assert "42" in eval_res


@pytest.mark.asyncio
async def test_phase8_headless_client() -> None:
    """Test Phase 8 tools with HeadlessCLIClient."""
    cfg = GodotConfig()
    client = HeadlessCLIClient(cfg)

    # 1. Get Autoloads headlessly
    auto_res = await handle_get_autoloads(client, GetAutoloadsInput())
    assert "Autoload Singletons" in auto_res

    # 2. Set Autoload headlessly
    set_res = await handle_set_autoload(
        client,
        SetAutoloadInput(
            name="ScoreKeeper",
            path="res://scripts/score_keeper.gd",
        ),
    )
    assert "ScoreKeeper" in set_res

    # 3. Get Node Signals headlessly
    sig_res = await handle_get_node_signals(
        client,
        GetNodeSignalsInput(node_path="/root/Main/Player"),
    )
    assert "Signals on `Player`" in sig_res

    # 4. Connect Signal headlessly
    conn_res = await handle_connect_signal(
        client,
        ConnectSignalInput(
            source_node_path="/root/Main/Player",
            signal_name="health_depleted",
            target_node_path="/root/Main/GameManager",
            method_name="_on_player_death",
        ),
    )
    assert "Signal Connected" in conn_res

    # 5. Evaluate Expression headlessly
    eval_res = await handle_evaluate_expression(
        client,
        EvaluateExpressionInput(
            expression="10 + 20 * 2",
        ),
    )
    assert "50" in eval_res
