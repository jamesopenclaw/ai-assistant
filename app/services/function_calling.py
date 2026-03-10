import asyncio
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

DB_PATH = "/tmp/chat_history.db"


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[..., Awaitable[Dict[str, Any]]]
    args_schema: Dict[str, Any] | None = None


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "args_schema": t.args_schema,
            }
            for t in self._tools.values()
        ]

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]


class FunctionCaller:
    def __init__(self, registry: ToolRegistry, db_path: str = DB_PATH, max_retries: int = 1):
        self.registry = registry
        self.db_path = db_path
        self.max_retries = max(0, max_retries)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                args_json TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_call_logs_tool_name ON tool_call_logs(tool_name)")
        conn.commit()
        conn.close()

    def _validate_args(self, tool: Tool, args: Dict[str, Any]):
        schema = tool.args_schema or {}
        if not schema:
            return

        if schema.get("type") == "object" and not isinstance(args, dict):
            raise ValueError("args must be an object")

        required = schema.get("required", [])
        for field in required:
            if field not in args:
                raise ValueError(f"missing required arg: {field}")

        properties = schema.get("properties", {})
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }

        for key, value in args.items():
            if key not in properties:
                continue
            field_schema = properties[key]
            expected_type = field_schema.get("type")
            if expected_type in type_map and not isinstance(value, type_map[expected_type]):
                raise ValueError(f"arg '{key}' should be {expected_type}")

            if expected_type in {"integer", "number"}:
                if "minimum" in field_schema and value < field_schema["minimum"]:
                    raise ValueError(f"arg '{key}' should be >= {field_schema['minimum']}")
                if "maximum" in field_schema and value > field_schema["maximum"]:
                    raise ValueError(f"arg '{key}' should be <= {field_schema['maximum']}")

    async def call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            tool = self.registry.get(tool_name)
        except KeyError as e:
            await self._log(tool_name, args, "error", None, str(e))
            return {"ok": False, "tool": tool_name, "error": str(e)}

        try:
            self._validate_args(tool, args)
        except Exception as e:
            await self._log(tool_name, args, "error", None, f"schema_validation_failed: {e}")
            return {"ok": False, "tool": tool_name, "error": f"schema_validation_failed: {e}"}

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = await tool.handler(**args)
                await self._log(tool_name, args, "success", result, None)
                return {"ok": True, "tool": tool_name, "result": result}
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    await asyncio.sleep(min(0.5 * (attempt + 1), 2.0))
                    continue

        await self._log(tool_name, args, "error", None, last_error)
        return {"ok": False, "tool": tool_name, "error": last_error}

    async def _log(self, tool_name: str, args: Dict[str, Any], status: str, result: Dict[str, Any] | None, error: str | None):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._log_sync, tool_name, args, status, result, error)

    def _log_sync(self, tool_name: str, args: Dict[str, Any], status: str, result: Dict[str, Any] | None, error: str | None):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO tool_call_logs (tool_name, args_json, status, result_json, error_message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                tool_name,
                json.dumps(args, ensure_ascii=False),
                status,
                json.dumps(result, ensure_ascii=False) if result is not None else None,
                error,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()
