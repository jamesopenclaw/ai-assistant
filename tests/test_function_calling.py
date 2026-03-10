import sqlite3
import pytest

from app.services.function_calling import FunctionCaller, ToolRegistry, Tool


@pytest.mark.asyncio
async def test_function_call_success_and_log(tmp_path):
    db_path = str(tmp_path / "tool_logs.db")
    registry = ToolRegistry()

    async def hello(name: str):
        return {"greeting": f"hi {name}"}

    registry.register(Tool(name="hello", description="say hi", handler=hello))
    caller = FunctionCaller(registry, db_path=db_path)

    result = await caller.call("hello", {"name": "linus"})
    assert result["ok"] is True
    assert result["result"]["greeting"] == "hi linus"

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT tool_name, status FROM tool_call_logs").fetchone()
    conn.close()
    assert row[0] == "hello"
    assert row[1] == "success"


@pytest.mark.asyncio
async def test_function_call_tool_not_found(tmp_path):
    db_path = str(tmp_path / "tool_logs.db")
    caller = FunctionCaller(ToolRegistry(), db_path=db_path)

    result = await caller.call("missing", {})
    assert result["ok"] is False
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_function_call_schema_validation_fail(tmp_path):
    db_path = str(tmp_path / "tool_logs.db")
    registry = ToolRegistry()

    async def hello(name: str):
        return {"greeting": f"hi {name}"}

    registry.register(
        Tool(
            name="hello",
            description="say hi",
            args_schema={
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}},
            },
            handler=hello,
        )
    )
    caller = FunctionCaller(registry, db_path=db_path)

    result = await caller.call("hello", {})
    assert result["ok"] is False
    assert "schema_validation_failed" in result["error"]


@pytest.mark.asyncio
async def test_function_call_retry_success(tmp_path):
    db_path = str(tmp_path / "tool_logs.db")
    registry = ToolRegistry()
    state = {"attempt": 0}

    async def flaky():
        state["attempt"] += 1
        if state["attempt"] == 1:
            raise RuntimeError("temporary")
        return {"ok": True}

    registry.register(Tool(name="flaky", description="flaky tool", handler=flaky))
    caller = FunctionCaller(registry, db_path=db_path, max_retries=1)

    result = await caller.call("flaky", {})
    assert result["ok"] is True
    assert state["attempt"] == 2
