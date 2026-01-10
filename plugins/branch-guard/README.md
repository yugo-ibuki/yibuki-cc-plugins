# Branch Guard Plugin

ブランチ名の命名規約を強制するガードレールプラグイン。

## 機能

- ブランチ作成時に命名規約をチェック
- main/masterへの直接pushをブロック
- 規約違反時にわかりやすいエラーメッセージを表示

## 許可されるブランチ名

| プレフィックス | 用途 | 例 |
|--------------|------|-----|
| `feature/` | 新機能 | `feature/add-login` |
| `fix/` | バグ修正 | `fix/null-pointer` |
| `hotfix/` | 緊急修正 | `hotfix/security-patch` |
| `chore/` | 雑務・設定変更 | `chore/update-deps` |
| `docs/` | ドキュメント | `docs/update-readme` |
| `refactor/` | リファクタリング | `refactor/clean-utils` |
| `test/` | テスト追加 | `test/add-unit-tests` |

## インストール

### 1. プラグインをインストール

```bash
claude plugins:install yugo-ibuki/yibuki-cc-plugins/plugins/branch-guard
```

### 2. 手動セットアップ（代替）

プロジェクトの `.claude/settings.json` に以下を追加:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/branch-validator.sh"
          }
        ]
      }
    ]
  }
}
```

`hooks/branch-validator.sh` をプロジェクトの `.claude/hooks/` にコピー:

```bash
mkdir -p .claude/hooks
cp path/to/branch-validator.sh .claude/hooks/
chmod +x .claude/hooks/branch-validator.sh
```

## 動作例

### ブロックされる場合

```bash
$ git checkout -b my-branch
========================================
 Branch Name Validation Error
========================================

ブランチ名が命名規約に違反しています: my-branch

許可されるフォーマット:
  - feature/<name>  : 新機能
  - fix/<name>      : バグ修正
  ...
```

### 許可される場合

```bash
$ git checkout -b feature/add-login
# 正常に実行
```

## カスタマイズ

`hooks/branch-validator.sh` の `ALLOWED_PATTERN` を編集して、
プロジェクト固有のルールを追加できます:

```bash
# 例: issue番号を必須にする
ALLOWED_PATTERN='^(feature|fix)/[A-Z]+-[0-9]+-[a-z0-9-]+$'
# → feature/PROJ-123-add-login
```

## 依存関係

- `jq` (JSONパース用)
