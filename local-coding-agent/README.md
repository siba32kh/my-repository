# ローカルLLMコーディングエージェント

ローカルLLM（自分のPC上で動くAI）を使って、**Claude Code風のコーディングアシスタント**を無料で動かすためのツールです。

---

## 目次

1. [必要なもの](#必要なもの)
2. [Step 1: Ollama のインストール](#step-1-ollama-のインストール)
3. [Step 2: AIモデルのダウンロード](#step-2-aiモデルのダウンロード)
4. [Step 3: Python環境の準備](#step-3-python環境の準備)
5. [Step 4: エージェントの起動](#step-4-エージェントの起動)
6. [使い方・コマンド一覧](#使い方コマンド一覧)
7. [スキル（スラッシュコマンド）](#スキルスラッシュコマンド)
8. [推奨モデル一覧](#推奨モデル一覧)
9. [別のLLMツールを使う場合](#別のllmツールを使う場合)
10. [トラブルシューティング](#トラブルシューティング)

---

## 必要なもの

| 項目 | 要件 |
|------|------|
| OS | Windows 10/11 / macOS / Linux |
| GPU | NVIDIA GPU（VRAM 8GB以上推奨） |
| RAM | 16GB以上推奨 |
| Python | 3.10以上 |
| ストレージ | モデルファイル用に10GB以上の空き |

> **GPUなしでも動きます**（CPUのみの場合は応答が遅くなります）

---

## Step 1: Ollama のインストール

**Ollama** はローカルLLMを簡単に動かすためのツールです。まずこれをインストールします。

### Windows / macOS
1. [https://ollama.com](https://ollama.com) にアクセス
2. **Download** ボタンからインストーラーをダウンロード
3. インストーラーを実行してインストール完了

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### インストール確認
ターミナル（コマンドプロンプト）を開いて以下を実行:

```bash
ollama --version
```

バージョン番号が表示されれば成功です。

---

## Step 2: AIモデルのダウンロード

Ollama でAIモデルをダウンロードします。**コーディング用に最適化されたモデル**を推奨します。

### 推奨: RTX 5070（VRAM 12GB）の場合

```bash
# 推奨モデル（コーディング特化・高精度）
ollama pull qwen2.5-coder:14b
```

ダウンロードには数分〜10分程度かかります（約9GB）。

### 軽量版（速度優先の場合）

```bash
# 小さいモデル（応答が速い・約5GB）
ollama pull qwen2.5-coder:7b
```

### ダウンロード確認

```bash
ollama list
```

ダウンロードしたモデルの一覧が表示されます。

---

## Step 3: Python環境の準備

### Python のインストール確認

```bash
python --version
# または
python3 --version
```

`Python 3.10.x` 以上が表示されればOKです。  
インストールされていない場合は [python.org](https://python.org) からダウンロードしてください。

### エージェントのセットアップ

```bash
# このリポジトリのフォルダへ移動
cd local-coding-agent

# 必要なパッケージをインストール
pip install -r requirements.txt
```

---

## Step 4: エージェントの起動

```bash
# デフォルト（qwen2.5-coder:7b）で起動
python main.py

# 推奨モデル（14b）で起動
python main.py --model ollama/qwen2.5-coder:14b
```

以下のような画面が表示されれば起動成功です:

```
╭─────────────────────────────────────────╮
│ ローカルLLMコーディングエージェント         │
│ モデル: ollama/qwen2.5-coder:14b          │
│ 作業ディレクトリ: /your/project/path       │
│ /help でヘルプ、/exit で終了               │
╰─────────────────────────────────────────╯

You>
```

---

## 使い方・コマンド一覧

### 基本的な使い方

`You>` のプロンプトに自然な日本語（または英語）で指示を入力します。

```
You> main.py を読んで内容を説明して

You> src/utils.py のバグを修正して

You> ls -la を実行して

You> 新しいファイル hello.py を作って「Hello World」を出力するコードを書いて
```

### エージェントが自動で使うツール

エージェントは必要に応じて以下のツールを自動で呼び出します:

| ツール名 | できること |
|---------|-----------|
| `read_file` | ファイルの内容を読む |
| `write_file` | 新しいファイルを作る・上書きする |
| `edit_file` | ファイルの一部を書き換える |
| `glob_files` | パターンでファイルを検索する（例: `*.py`） |
| `grep_files` | ファイルの中身を正規表現で検索する |
| `bash` | シェルコマンドを実行する |
| `spawn_agent` | 並列で別のエージェントを動かす |

---

## スキル（スラッシュコマンド）

`/` で始まる特別なコマンドで、よく使う操作をワンコマンドで実行できます。

### `/help` — ヘルプ表示

```
You> /help
```

### `/commit` — git コミット

変更内容を自動で確認し、コミットメッセージを生成してコミットします。

```
You> /commit
```

実行内容:
1. `git status` で変更ファイルを確認
2. `git diff` で変更内容を読む
3. 適切なコミットメッセージを生成
4. `git add -A` → `git commit` を実行

### `/review [対象]` — コードレビュー

```
You> /review src/
You> /review main.py
You> /review          # 引数なしでカレントディレクトリ全体
```

セキュリティ・パフォーマンス・可読性などの観点からレビューします。

### `/exit` — 終了

```
You> /exit
```

`Ctrl + C` でも終了できます。

---

## 推奨モデル一覧

### GeForce RTX 5070（VRAM 12GB）の場合

| モデル | コマンド | VRAM | 特徴 |
|--------|---------|------|------|
| **qwen2.5-coder:14b** ⭐ | `ollama pull qwen2.5-coder:14b` | ~8.5GB | **最推奨**。コーディング特化・高精度 |
| qwen2.5-coder:7b | `ollama pull qwen2.5-coder:7b` | ~4.5GB | 高速。デフォルト設定 |
| deepseek-coder-v2:16b | `ollama pull deepseek-coder-v2:16b` | ~10GB | 推論力が高い |
| llama3.1:8b | `ollama pull llama3.1:8b` | ~5GB | 汎用・tool use対応 |

### VRAMが少ない場合（8GB以下）

| モデル | コマンド | VRAM | 特徴 |
|--------|---------|------|------|
| qwen2.5-coder:7b | `ollama pull qwen2.5-coder:7b` | ~4.5GB | 8GB以上で快適 |
| llama3.2:3b | `ollama pull llama3.2:3b` | ~2GB | 非常に軽量 |

### デフォルトモデルの変更方法

`config.py` を編集します:

```python
# config.py の4行目あたり
MODEL = os.getenv("AGENT_MODEL", "ollama/qwen2.5-coder:14b")  # ここを変更
```

または起動時に指定:

```bash
python main.py --model ollama/qwen2.5-coder:14b
```

---

## 別のLLMツールを使う場合

### LM Studio

1. [LM Studio](https://lmstudio.ai/) をダウンロード・インストール
2. アプリ内でモデルをダウンロード
3. 「Local Server」を起動（デフォルトポート: 1234）
4. 以下のコマンドで起動:

```bash
python main.py --model openai/local --base-url http://localhost:1234/v1
```

### llama.cpp（上級者向け）

```bash
python main.py --model openai/local --base-url http://localhost:8080/v1
```

### Anthropic Claude（有料APIを使う場合）

```bash
# APIキーを設定して起動
python main.py --model anthropic/claude-opus-4-6 --api-key sk-ant-xxxxxxxx
```

---

## 設定（環境変数）

`.env` ファイルを作成するか、ターミナルで環境変数を設定できます:

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `AGENT_MODEL` | 使用するモデル名 | `ollama/qwen2.5-coder:7b` |
| `AGENT_BASE_URL` | LLMのエンドポイントURL | 自動（Ollama） |
| `AGENT_API_KEY` | APIキー | なし |
| `AGENT_MAX_TURNS` | 1回の会話の最大ターン数 | `30` |
| `AGENT_WORKING_DIR` | 作業ディレクトリ | 起動したディレクトリ |
| `AGENT_BASH_TIMEOUT` | Bashコマンドのタイムアウト（秒） | `30` |

### 設定例（Windowsのコマンドプロンプト）

```cmd
set AGENT_MODEL=ollama/qwen2.5-coder:14b
python main.py
```

### 設定例（macOS / Linux）

```bash
export AGENT_MODEL=ollama/qwen2.5-coder:14b
python main.py
```

---

## トラブルシューティング

### `ollama: command not found`

Ollama がインストールされていません。[Step 1](#step-1-ollama-のインストール) からやり直してください。

### `Error: model not found`

モデルがダウンロードされていません。以下を実行してください:

```bash
ollama pull qwen2.5-coder:7b
```

### `Connection refused` / `LLMに接続できない`

Ollama が起動していない可能性があります。

```bash
# Ollamaを手動で起動
ollama serve
```

別のターミナルでエージェントを起動してください。

### `pip install -r requirements.txt` でエラー

Python のバージョンを確認してください:

```bash
python --version  # 3.10以上が必要
```

古い場合は [python.org](https://python.org) から最新版をインストールしてください。

### 応答が遅い

- より小さいモデル（`qwen2.5-coder:7b`）を試してください
- GPU が使われているか確認:

```bash
# Ollamaのログを確認（GPUが使われているか）
ollama run qwen2.5-coder:7b "hello"
```

NVIDIA GPU がある場合、Ollama は自動でGPUを使います。

---

## ファイル構成

```
local-coding-agent/
├── main.py              # エントリポイント（ここから起動）
├── config.py            # 設定ファイル
├── requirements.txt     # 必要なPythonパッケージ
└── agent/
    ├── core.py          # エージェントのメインループ
    ├── llm/
    │   └── client.py    # LLM通信クライアント
    ├── tools/
    │   ├── file_tools.py   # ファイル操作ツール
    │   ├── bash_tool.py    # Bash実行ツール
    │   └── agent_tool.py   # サブエージェントツール
    └── skills/
        ├── registry.py     # スキル管理
        └── builtin/
            ├── commit.py   # /commit スキル
            └── review.py   # /review スキル
```
