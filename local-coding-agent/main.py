#!/usr/bin/env python3
"""
ローカルLLMコーディングエージェント — CLIエントリポイント

使い方:
    python main.py
    python main.py --model ollama/llama3.2
    python main.py --model openai/local --base-url http://localhost:1234/v1
    AGENT_MODEL=anthropic/claude-opus-4-6 python main.py
"""

from __future__ import annotations

import argparse
import sys

import anyio
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

import config
from agent.core import run_agent
from agent.llm.client import LLMClient
from agent.tools import get_tool_schemas
from agent.skills import registry as skill_registry

console = Console()

HELP_TEXT = """
## 使い方

通常のメッセージを入力するとエージェントが応答します。

## スキル（スラッシュコマンド）

| コマンド | 説明 |
|---------|------|
| `/help` | このヘルプを表示 |
| `/commit` | git変更をコミット |
| `/review [対象]` | コードレビュー |
| `/exit` | 終了 |

## ツール

エージェントは以下のツールを使えます:
- **read_file** — ファイル読み込み
- **write_file** — ファイル作成・上書き
- **edit_file** — ファイル差分編集
- **glob_files** — ファイルパターン検索
- **grep_files** — 内容正規表現検索
- **bash** — シェルコマンド実行
- **spawn_agent** — サブエージェント起動（並列実行）

## 設定（環境変数）

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `AGENT_MODEL` | LLMモデル名 | `ollama/qwen2.5-coder:7b` |
| `AGENT_BASE_URL` | LLMエンドポイント | （自動） |
| `AGENT_API_KEY` | APIキー | （なし） |
| `AGENT_MAX_TURNS` | 最大ターン数 | `30` |
| `AGENT_WORKING_DIR` | 作業ディレクトリ | カレントディレクトリ |
"""


def print_banner(model: str) -> None:
    console.print(Panel(
        f"[bold cyan]ローカルLLMコーディングエージェント[/bold cyan]\n"
        f"モデル: [yellow]{model}[/yellow]\n"
        f"作業ディレクトリ: [dim]{config.WORKING_DIR}[/dim]\n"
        f"[dim]/help でヘルプ、/exit で終了[/dim]",
        border_style="cyan",
    ))


async def chat_loop(llm: LLMClient) -> None:
    all_tools = get_tool_schemas()

    while True:
        try:
            user_input = console.input("\n[bold green]You>[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]終了します。[/dim]")
            break

        if not user_input:
            continue

        # --- 組み込みコマンド ---
        if user_input in ("/exit", "/quit", "exit", "quit"):
            console.print("[dim]終了します。[/dim]")
            break

        if user_input == "/help":
            console.print(Markdown(HELP_TEXT))
            continue

        # --- スキル解決 ---
        skill_match = skill_registry.resolve(user_input)
        if skill_match is not None:
            skill, prompt = skill_match
            console.print(f"[dim]スキル実行: /{skill.name}[/dim]")
            tool_schemas = get_tool_schemas(skill.tools) if skill.tools else all_tools
        elif user_input.startswith("/"):
            # 未知のスラッシュコマンド
            skill_name = user_input[1:].split()[0]
            console.print(f"[red]不明なスキル: /{skill_name}[/red]  (/help でスキル一覧確認)")
            continue
        else:
            prompt = user_input
            tool_schemas = all_tools

        # --- エージェント実行 ---
        try:
            result = await run_agent(
                prompt=prompt,
                llm=llm,
                tool_schemas=tool_schemas,
            )
        except Exception as e:
            console.print(f"[red]エラー: {e}[/red]")
            continue

        if result:
            console.print("\n[bold]Assistant>[/bold]")
            console.print(Markdown(result))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ローカルLLMコーディングエージェント",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help=f"LLMモデル名 (デフォルト: {config.MODEL})",
    )
    parser.add_argument(
        "--base-url", "-u",
        default=None,
        dest="base_url",
        help="LLMエンドポイントURL",
    )
    parser.add_argument(
        "--api-key", "-k",
        default=None,
        dest="api_key",
        help="APIキー",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    model = args.model or config.MODEL
    base_url = args.base_url or config.BASE_URL
    api_key = args.api_key or config.API_KEY

    llm = LLMClient(model=model, base_url=base_url, api_key=api_key)

    print_banner(model)
    await chat_loop(llm)


if __name__ == "__main__":
    anyio.run(main)
