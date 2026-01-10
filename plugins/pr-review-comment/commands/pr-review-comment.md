---
allowed-tools:
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(gh pr:*)
  - Bash(gh api:*)
  - Read
  - Glob
argument-hint: [PR番号 or ブランチ名]
description: PRの変更点をまとめるコメントを作成
model: claude-3-5-haiku-20241022
---

# PR Review Comment

PRの変更点を分析し、やったことをまとめるコメントを作成します。

## Rules

- `./.github/` 配下に pull_request_template.md 関連のファイルがあればそのフォーマットに合わせる
  - プロジェクトにPRテンプレートがない場合、`./.claude/pr-review-comment/assets/PR_TEMPLATE.md` を参照
- テンプレートの項目に沿って変更内容をまとめる
- 日本語で作成する
- 変更の「何をしたか」に焦点を当てる

## Workflow

1. **PRテンプレートの確認**
   - `./.github/pull_request_template.md` の存在確認
   - なければ `./.claude/pr-review-comment/assets/PR_TEMPLATE.md` を使用

2. **変更内容の取得**
   - 引数がある場合:
     - PR番号なら `gh pr diff $ARGUMENTS` で取得
     - ブランチ名なら `git diff main...$ARGUMENTS` で取得
   - 引数がない場合:
     - `git diff main...HEAD` でローカル変更を取得

3. **変更ファイルの分析**
   - 追加・削除・変更された内容を確認
   - 変更の意図を理解
   - 機能単位でグルーピング

4. **コメント生成**
   - テンプレートのフォーマットに沿って出力
   - 各セクションを適切に埋める

## 出力例

```markdown
## 概要

認証機能にOAuth2サポートを追加

## やったこと

- OAuth2認証プロバイダーを実装
- ログイン画面にソーシャルログインボタンを追加
- セッション管理を改善

## 懸念点

- リフレッシュトークンの有効期限設定が適切か要確認
```

## 注意点

- 技術的詳細より機能・目的を重視
- 簡潔で分かりやすい表現を使う
- テンプレートにない項目は追加しない
