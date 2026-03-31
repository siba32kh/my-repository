from .commit import COMMIT_SKILL
from .review import REVIEW_SKILL
from ..registry import SkillRegistry


def register_builtin_skills(registry: SkillRegistry) -> None:
    registry.register(COMMIT_SKILL)
    registry.register(REVIEW_SKILL)
