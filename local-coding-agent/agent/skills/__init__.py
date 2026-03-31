from .registry import SkillRegistry, Skill
from .builtin import register_builtin_skills

registry = SkillRegistry()
register_builtin_skills(registry)
