from agent.skills.registry import Skill

REVIEW_SKILL = Skill(
    name="review",
    description="指定したファイル/ディレクトリのコードレビューを行う",
    tools=["read_file", "glob_files", "grep_files"],
    aliases=["cr"],
    prompt_template="""\
以下の対象をコードレビューしてください。

対象: {args_or_empty}

レビュー観点:
1. バグや潜在的な不具合
2. セキュリティの問題
3. パフォーマンスの問題
4. コードの可読性・保守性
5. ベストプラクティスへの準拠

まずファイル一覧を確認し、重要なファイルを読んでからレビュー結果をまとめてください。
""",
)
