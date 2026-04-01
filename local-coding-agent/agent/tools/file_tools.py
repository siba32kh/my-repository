"""
ファイル操作ツール: Read / Write / Edit / Glob / Grep
"""

from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path
from typing import Any

import config


# ---------------------------------------------------------------------------
# ツール実装
# ---------------------------------------------------------------------------

def _resolve(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = Path(config.WORKING_DIR) / p
    return p.resolve()


def read_file(path: str, offset: int = 0, limit: int = 200) -> str:
    """ファイルを読み込んで行番号付きで返す。"""
    resolved = _resolve(path)
    if not resolved.exists():
        return f"エラー: ファイルが見つかりません: {path}"
    if not resolved.is_file():
        return f"エラー: パスはファイルではありません: {path}"

    lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
    total = len(lines)
    sliced = lines[offset : offset + limit]
    result_lines = [f"{offset + i + 1}\t{line}" for i, line in enumerate(sliced)]

    header = f"# {path} ({total} 行中 {offset + 1}–{offset + len(sliced)} 行を表示)\n"
    return header + "\n".join(result_lines)


def write_file(path: str, content: str) -> str:
    """ファイルを新規作成または上書きする。"""
    resolved = _resolve(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")
    return f"書き込み完了: {path} ({len(content.splitlines())} 行)"


def edit_file(path: str, old_string: str, new_string: str) -> str:
    """ファイル内の文字列を置換する（1回だけ）。"""
    resolved = _resolve(path)
    if not resolved.exists():
        return f"エラー: ファイルが見つかりません: {path}"

    content = resolved.read_text(encoding="utf-8")
    if old_string not in content:
        return f"エラー: 対象文字列が見つかりません:\n{old_string}"

    count = content.count(old_string)
    if count > 1:
        return (
            f"エラー: 対象文字列が {count} 箇所に存在します。"
            "一意に特定できる文字列を指定してください。"
        )

    new_content = content.replace(old_string, new_string, 1)
    resolved.write_text(new_content, encoding="utf-8")
    return f"編集完了: {path}"


def glob_files(pattern: str, path: str = ".") -> str:
    """パターンに一致するファイルパスを返す。"""
    base = _resolve(path)
    if not base.exists():
        return f"エラー: ディレクトリが見つかりません: {path}"

    matches = sorted(str(p.relative_to(base)) for p in base.rglob("*")
                     if p.is_file() and fnmatch.fnmatch(p.name, pattern.split("/")[-1]))

    # ダブルスターを含む場合はrglob側で処理済み
    if not matches:
        return f"一致するファイルなし: {pattern}"
    return "\n".join(matches)


def grep_files(pattern: str, path: str = ".", file_glob: str = "**/*") -> str:
    """ファイル内容を正規表現で検索し、マッチした行を返す。"""
    base = _resolve(path)
    if not base.exists():
        return f"エラー: ディレクトリが見つかりません: {path}"

    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"エラー: 無効な正規表現: {e}"

    results: list[str] = []
    for p in sorted(base.rglob("*")):
        if not p.is_file():
            continue
        if not fnmatch.fnmatch(str(p.relative_to(base)), file_glob):
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                rel = str(p.relative_to(base))
                results.append(f"{rel}:{i}:{line}")

    if not results:
        return f"一致なし: {pattern}"
    return "\n".join(results[:500])  # 上限500行


# ---------------------------------------------------------------------------
# JSON Schema 定義
# ---------------------------------------------------------------------------

FILE_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "ファイルを読み込んで内容を返す。行番号付き。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "読み込むファイルパス"},
                    "offset": {"type": "integer", "description": "開始行（0始まり）", "default": 0},
                    "limit": {"type": "integer", "description": "読み込む最大行数", "default": 200},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "ファイルを新規作成または上書きする。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "書き込むファイルパス"},
                    "content": {"type": "string", "description": "ファイルの内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "ファイル内の特定の文字列を別の文字列に置換する。対象は一意である必要がある。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "編集するファイルパス"},
                    "old_string": {"type": "string", "description": "置換前の文字列（完全一致、一意であること）"},
                    "new_string": {"type": "string", "description": "置換後の文字列"},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "パターンに一致するファイルの一覧を返す。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "グロブパターン（例: *.py, **/*.ts）"},
                    "path": {"type": "string", "description": "検索するベースディレクトリ", "default": "."},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_files",
            "description": "ファイル内容を正規表現で検索し、マッチした行を返す。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "検索する正規表現"},
                    "path": {"type": "string", "description": "検索するベースディレクトリ", "default": "."},
                    "file_glob": {"type": "string", "description": "対象ファイルのグロブパターン", "default": "**/*"},
                },
                "required": ["pattern"],
            },
        },
    },
]


def execute_file_tool(name: str, args: dict[str, Any]) -> str:
    """ファイルツールを名前で呼び出す。"""
    dispatch = {
        "read_file": read_file,
        "write_file": write_file,
        "edit_file": edit_file,
        "glob_files": glob_files,
        "grep_files": grep_files,
    }
    fn = dispatch.get(name)
    if fn is None:
        return f"不明なファイルツール: {name}"
    return fn(**args)
