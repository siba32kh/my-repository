"""
メインエージェントループ。
LLMにツールスキーマを渡し、tool_callsが返ってくる限りツールを実行し続ける。
"""

from __future__ import annotations

import json
from typing import Any

import anyio
from rich.console import Console

import config
from agent.llm.client import LLMClient, LLMResponse
from agent.tools.file_tools import execute_file_tool
from agent.tools.bash_tool import execute_bash_tool

console = Console()

_FILE_TOOL_NAMES = {"read_file", "write_file", "edit_file", "glob_files", "grep_files"}
_BASH_TOOL_NAMES = {"bash"}
_AGENT_TOOL_NAMES = {"spawn_agent"}


async def run_agent(
    prompt: str,
    llm: LLMClient,
    tool_schemas: list[dict],
    label: str = "",
    max_turns: int | None = None,
) -> str:
    """
    エージェントループ。
    - LLMにメッセージを送る
    - tool_calls があればツールを実行してフィードバック
    - tool_calls がなければ終了
    """
    if max_turns is None:
        max_turns = config.MAX_TURNS

    messages: list[dict] = [{"role": "user", "content": prompt}]
    prefix = f"{label} " if label else ""

    for turn in range(max_turns):
        console.print(f"[dim]{prefix}LLMに送信中... (ターン {turn + 1}/{max_turns})[/dim]")

        response: LLMResponse = await llm.achat(messages, tool_schemas or None)

        # アシスタントの返答をメッセージ履歴に追加
        assistant_msg: dict[str, Any] = {"role": "assistant"}
        if response.content:
            assistant_msg["content"] = response.content
        if response.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
                }
                for tc in response.tool_calls
            ]
        messages.append(assistant_msg)

        if not response.tool_calls:
            # ツール呼び出しなし → 最終回答
            return response.content or ""

        # ツールを並列実行
        tool_results = await _execute_tools_parallel(
            response.tool_calls, llm, tool_schemas, prefix
        )

        # ツール結果をメッセージ履歴に追加
        for tc, result in zip(response.tool_calls, tool_results):
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return f"最大ターン数 ({max_turns}) に達しました。処理を中断します。"


async def _execute_tools_parallel(tool_calls, llm, tool_schemas, prefix) -> list[str]:
    """複数のツール呼び出しを並列実行する。"""
    results: list[str] = [""] * len(tool_calls)

    async def run_one(index: int, tc) -> None:
        console.print(
            f"[cyan]{prefix}ツール実行:[/cyan] [bold]{tc.name}[/bold] "
            f"[dim]{_summarize_args(tc.arguments)}[/dim]"
        )
        result = await _execute_single_tool(tc.name, tc.arguments, llm, tool_schemas)
        results[index] = result
        # 結果のプレビューを表示（長すぎる場合は省略）
        preview = result[:200] + "..." if len(result) > 200 else result
        console.print(f"[green]{prefix}→ {tc.name}:[/green] {preview}")

    async with anyio.create_task_group() as tg:
        for i, tc in enumerate(tool_calls):
            tg.start_soon(run_one, i, tc)

    return results


async def _execute_single_tool(
    name: str,
    args: dict[str, Any],
    llm: LLMClient,
    tool_schemas: list[dict],
) -> str:
    """ツール名に応じて適切な実装を呼び出す。"""
    try:
        if name in _FILE_TOOL_NAMES:
            # ファイルツールは同期だが anyio で wrap
            return await anyio.to_thread.run_sync(
                lambda: execute_file_tool(name, args)
            )
        elif name in _BASH_TOOL_NAMES:
            return await anyio.to_thread.run_sync(
                lambda: execute_bash_tool(name, args)
            )
        elif name in _AGENT_TOOL_NAMES:
            from agent.tools.agent_tool import execute_agent_tool
            return await execute_agent_tool(name, args, llm, tool_schemas)
        else:
            return f"不明なツール: {name}"
    except Exception as e:
        return f"ツール実行エラー ({name}): {e}"


def _summarize_args(args: dict) -> str:
    """引数の短い説明文を生成する。"""
    if not args:
        return ""
    items = [f"{k}={repr(v)[:40]}" for k, v in list(args.items())[:3]]
    return ", ".join(items)
