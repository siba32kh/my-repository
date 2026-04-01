from agent.skills.registry import Skill

COMMIT_SKILL = Skill(
    name="commit",
    description="git の変更内容を確認し、コミットメッセージを生成してコミットする",
    tools=["bash"],
    prompt_template="""\
以下の手順でgitコミットを行ってください。

1. `git status` を実行して変更ファイルを確認する
2. `git diff` を実行して変更内容を把握する
3. 変更内容に基づいて適切なコミットメッセージを考える
   - 1行目: 変更の要約（50文字以内、日本語可）
   - 必要なら空行の後に詳細説明
4. `git add -A` でステージングする
5. `git commit -m "メッセージ"` でコミットする
6. コミット結果を報告する

追加の引数: {args_or_empty}
""",
)
