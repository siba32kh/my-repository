import os

# --- LLMモデル設定 ---
# 環境変数 AGENT_MODEL で上書き可能
# 例:
#   Ollama:     ollama/qwen2.5-coder:7b  (デフォルト)
#   LM Studio:  openai/local-model  + AGENT_BASE_URL=http://localhost:1234/v1
#   llama.cpp:  openai/local         + AGENT_BASE_URL=http://localhost:8080/v1
#   Anthropic:  anthropic/claude-opus-4-6
MODEL = os.getenv("AGENT_MODEL", "ollama/qwen2.5-coder:7b")

# ローカルLLMのエンドポイント（Ollamaはlitellmが自動検出するのでNone可）
BASE_URL = os.getenv("AGENT_BASE_URL", None)

# APIキー（Anthropicや有料サービスを使う場合に設定）
API_KEY = os.getenv("AGENT_API_KEY", None)

# --- エージェント設定 ---
MAX_TURNS = int(os.getenv("AGENT_MAX_TURNS", "30"))
WORKING_DIR = os.getenv("AGENT_WORKING_DIR", os.getcwd())

# ツール実行のタイムアウト（秒）
BASH_TIMEOUT = int(os.getenv("AGENT_BASH_TIMEOUT", "30"))

# サブエージェントの最大並列数
MAX_SUBAGENTS = int(os.getenv("AGENT_MAX_SUBAGENTS", "5"))
