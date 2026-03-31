"""
Bashコマンド実行ツール
"""

from __future__ import annotations

import subprocess
from typing import Any

import config


BASH_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "シェルコマンドを実行し、stdout/stderr/終了コードを返す。",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "実行するシェルコマンド",
                },
                "timeout": {
                    "type": "integer",
                    "description": "タイムアウト秒数（デフォルト30）",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
    },
}


def execute_bash_tool(name: str, args: dict[str, Any]) -> str:
    if name != "bash":
        return f"不明なツール: {name}"
    return bash(**args)


def bash(command: str, timeout: int | None = None) -> str:
    """コマンドを実行して結果を返す。"""
    if timeout is None:
        timeout = config.BASH_TIMEOUT

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=config.WORKING_DIR,
        )
    except subprocess.TimeoutExpired:
        return f"エラー: タイムアウト ({timeout}秒)"
    except OSError as e:
        return f"エラー: {e}"

    parts: list[str] = []
    if result.stdout:
        parts.append(f"stdout:\n{result.stdout.rstrip()}")
    if result.stderr:
        parts.append(f"stderr:\n{result.stderr.rstrip()}")
    parts.append(f"exit code: {result.returncode}")
    return "\n".join(parts)
