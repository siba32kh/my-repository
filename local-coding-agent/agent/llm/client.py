"""
LiteLLMベースのLLMクライアント。
Ollama / LM Studio / llama.cpp / Anthropic / OpenAI など
任意のバックエンドを統一インターフェースで扱う。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import litellm

import config


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"


class LLMClient:
    """LiteLLMをラップしたシンプルなLLMクライアント。"""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        system_prompt: str | None = None,
    ):
        self.model = model or config.MODEL
        self.base_url = base_url or config.BASE_URL
        self.api_key = api_key or config.API_KEY
        self.system_prompt = system_prompt or _DEFAULT_SYSTEM_PROMPT

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        """LLMにメッセージを送信し、レスポンスを返す（同期版）。"""
        full_messages = self._build_messages(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": full_messages,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = litellm.completion(**kwargs)
        return self._parse_response(response)

    async def achat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        """LLMにメッセージを送信し、レスポンスを返す（非同期版）。"""
        full_messages = self._build_messages(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": full_messages,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await litellm.acompletion(**kwargs)
        return self._parse_response(response)

    def _build_messages(self, messages: list[dict]) -> list[dict]:
        if self.system_prompt:
            return [{"role": "system", "content": self.system_prompt}] + messages
        return messages

    @staticmethod
    def _parse_response(response) -> LLMResponse:
        choice = response.choices[0]
        message = choice.message
        finish_reason = choice.finish_reason or "stop"

        tool_calls: list[ToolCall] = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args,
                    )
                )

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
        )


_DEFAULT_SYSTEM_PROMPT = """\
あなたは優秀なコーディングアシスタントです。
ユーザーの依頼に対して、提供されたツールを使って正確に作業を行います。

## 行動指針
- ファイルを読む前に変更しない
- コマンド実行前にその内容を確認する
- 複数のタスクは並列サブエージェントを使って効率化する
- 作業完了後は結果を簡潔に報告する
"""
