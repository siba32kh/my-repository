"""
サブエージェント起動ツール。
複数のタスクを並列で実行するときに使う。
"""

from __future__ import annotations

from typing import Any


AGENT_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "spawn_agent",
        "description": (
            "独立したサブエージェントを起動して、別タスクを並列実行する。"
            "複数ファイルの同時解析や並列処理に使う。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "サブエージェントの役割・目的の説明（1行）",
                },
                "prompt": {
                    "type": "string",
                    "description": "サブエージェントに与えるタスク指示",
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "サブエージェントに許可するツール名のリスト。"
                        "省略時は親と同じツールセット。"
                    ),
                },
            },
            "required": ["description", "prompt"],
        },
    },
}


async def execute_agent_tool(
    name: str,
    args: dict[str, Any],
    llm_client,
    tool_schemas: list[dict],
) -> str:
    """spawn_agent を実行する（agent/core.py から呼ばれる）。"""
    if name != "spawn_agent":
        return f"不明なツール: {name}"

    # インポートをここで行い循環依存を避ける
    from agent.core import run_agent
    from agent.tools import get_tool_schemas

    description = args.get("description", "サブエージェント")
    prompt = args.get("prompt", "")
    allowed_tools = args.get("tools", None)

    sub_tools = get_tool_schemas(allowed_tools) if allowed_tools else tool_schemas

    result = await run_agent(
        prompt=prompt,
        llm=llm_client,
        tool_schemas=sub_tools,
        label=f"[subagent: {description}]",
    )
    return result or "(サブエージェントから応答なし)"
