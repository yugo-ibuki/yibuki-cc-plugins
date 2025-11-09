---
allowed-tools:
  - Bash(git add *)
  - Bash(git status *)
  - Bash(git commit *)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git branch *)
  - Bash(gh pr create *)
  - Bash(gh pr view *)
  - Read
argument-hint: [commit message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

# PR Creator

Git commitとPRを作成します。

## Rules

- PRはmainブランチから作成する
- `./.github/` 配下に pull_request_template.md 関連のファイルがあればそれをPR作成時に参照
  - プロジェクトにPRテンプレートがない場合、`./.claude/pr-creator/assets/PR_TEMPALATE.md` を参照
- PRのテンプレートにある内容は削除しない
- 日本語で作成する

## Workflow

1. **変更内容の確認**
   - `git status` で変更ファイルを確認
   - `git diff` で変更内容の詳細を確認

2. **コミット作成**
   - 変更をステージング: `git add .`
   - コミット作成: `git commit -m "$ARGUMENTS"`
   - コミットメッセージが未指定の場合、変更内容から適切なメッセージを生成

3. **ブランチの確認**
   - 現在のブランチを確認
   - mainブランチの場合は警告を出す

4. **PRテンプレートの確認**
   - `./.github/pull_request_template.md` の存在確認
   - なければ `./.claude/pr-creator/template.md` を使用

5. **PR作成**
   - `gh pr create` でPRを作成
   - テンプレートの内容を埋める
   - PRのURLを表示

## 注意点

- mainブランチへの直接コミットは避ける
- コミット前に必ずdiffを確認
- PRタイトルはコミットメッセージから生成
