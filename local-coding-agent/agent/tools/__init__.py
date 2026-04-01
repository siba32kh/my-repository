from .file_tools import FILE_TOOLS, execute_file_tool
from .bash_tool import BASH_TOOL, execute_bash_tool
from .agent_tool import AGENT_TOOL

ALL_TOOLS = FILE_TOOLS + [BASH_TOOL, AGENT_TOOL]


def get_tool_schemas(tool_names: list[str] | None = None) -> list[dict]:
    """指定されたツール名のスキーマ一覧を返す。Noneの場合は全ツール。"""
    if tool_names is None:
        return ALL_TOOLS
    name_set = set(tool_names)
    return [t for t in ALL_TOOLS if t["function"]["name"] in name_set]
