"""
スキル（スラッシュコマンド）の登録・ディスパッチ。

スキルは `/commit` のように `/` で始まる入力によって呼び出される。
各スキルは「プロンプトテンプレート」と「使用するツール名リスト」を持つ。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Skill:
    name: str                              # スキル名（/なし）例: "commit"
    description: str                       # 説明文
    prompt_template: str                   # エージェントに渡すプロンプトテンプレート
    tools: list[str] | None = None        # 使用するツール名。None=全ツール
    system_extra: str | None = None        # システムプロンプトへの追記
    aliases: list[str] = field(default_factory=list)


class SkillRegistry:
    """スキルを登録・管理するレジストリ。"""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill
        for alias in skill.aliases:
            self._skills[alias] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def list_skills(self) -> list[Skill]:
        """重複なしでスキル一覧を返す。"""
        seen: set[str] = set()
        result: list[Skill] = []
        for skill in self._skills.values():
            if skill.name not in seen:
                seen.add(skill.name)
                result.append(skill)
        return sorted(result, key=lambda s: s.name)

    def resolve(self, user_input: str) -> tuple[Skill, str] | None:
        """
        `/skillname [args]` 形式の入力を解析してスキルと引数を返す。
        スキルでない場合は None を返す。
        """
        stripped = user_input.strip()
        if not stripped.startswith("/"):
            return None

        parts = stripped[1:].split(None, 1)
        skill_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        skill = self.get(skill_name)
        if skill is None:
            return None

        prompt = skill.prompt_template.format(args=args, args_or_empty=args or "")
        return skill, prompt
