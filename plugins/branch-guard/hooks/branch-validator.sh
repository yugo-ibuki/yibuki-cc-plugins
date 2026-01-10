#!/bin/bash
#
# Branch Name Validator Hook
# ブランチ作成時に命名規約をチェック
#
set -euo pipefail

# 標準入力からJSON取得
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# git checkout -b または git switch -c でブランチ作成を検出
if echo "$COMMAND" | grep -qE 'git (checkout -b|switch -c) '; then
  # ブランチ名を抽出
  BRANCH=$(echo "$COMMAND" | grep -oE '(checkout -b|switch -c) [^ ]+' | awk '{print $NF}')

  # 許可するブランチ名パターン
  # feature/xxx, fix/xxx, hotfix/xxx, chore/xxx, docs/xxx, refactor/xxx, test/xxx
  ALLOWED_PATTERN='^(feature|fix|hotfix|chore|docs|refactor|test)/[a-z0-9][a-z0-9-]*$'

  if ! echo "$BRANCH" | grep -qE "$ALLOWED_PATTERN"; then
    echo "" >&2
    echo "========================================" >&2
    echo " Branch Name Validation Error" >&2
    echo "========================================" >&2
    echo "" >&2
    echo "ブランチ名が命名規約に違反しています: $BRANCH" >&2
    echo "" >&2
    echo "許可されるフォーマット:" >&2
    echo "  - feature/<name>  : 新機能" >&2
    echo "  - fix/<name>      : バグ修正" >&2
    echo "  - hotfix/<name>   : 緊急修正" >&2
    echo "  - chore/<name>    : 雑務・設定変更" >&2
    echo "  - docs/<name>     : ドキュメント" >&2
    echo "  - refactor/<name> : リファクタリング" >&2
    echo "  - test/<name>     : テスト追加" >&2
    echo "" >&2
    echo "例: feature/add-login, fix/null-pointer, docs/update-readme" >&2
    echo "========================================" >&2
    exit 2
  fi
fi

# mainやmasterへの直接push検出
if echo "$COMMAND" | grep -qE 'git push.*(origin|upstream) (main|master)($| )'; then
  echo "" >&2
  echo "========================================" >&2
  echo " Protected Branch Warning" >&2
  echo "========================================" >&2
  echo "" >&2
  echo "main/masterブランチへの直接pushは推奨されません。" >&2
  echo "PRを作成してマージしてください。" >&2
  echo "========================================" >&2
  exit 2
fi

exit 0
