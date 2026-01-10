---
name: explore-project
description: プロジェクト全体の構造を探索し、ディレクトリ構成、主要ファイル、アーキテクチャを把握する。プロジェクトに新しく参加したメンバーがプロジェクトを理解する際に自動的に呼び出される。
version: "1.0.0"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(ls:*)
  - Bash(tree:*)
  - Bash(find:*)
  - Bash(wc:*)
---

# explore-project スキル

プロジェクトの全体構造を探索し、新規参加者がプロジェクトを理解するための情報を収集します。

## 探索対象

### 1. プロジェクト設定ファイル

以下のファイルを優先的に確認:

- `README.md` / `README.*` - プロジェクト概要
- `CLAUDE.md` - Claude Code用の指示
- `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` - 依存関係・プロジェクト情報
- `.env.example` / `.env.sample` - 環境変数
- `Makefile` / `Dockerfile` / `docker-compose.yml` - ビルド・実行環境

### 2. ディレクトリ構造

```bash
# トップレベルのディレクトリ構造を取得
tree -L 2 -d --noreport

# ファイル数の多いディレクトリを特定
find . -type f | cut -d/ -f2 | sort | uniq -c | sort -rn | head -10
```

### 3. アーキテクチャパターンの特定

以下のパターンを検出:

- **フロントエンド**: `src/components/`, `src/pages/`, `app/`
- **バックエンド**: `src/controllers/`, `src/services/`, `src/routes/`
- **共通**: `src/utils/`, `src/lib/`, `src/helpers/`
- **テスト**: `tests/`, `__tests__/`, `spec/`
- **設定**: `config/`, `.config/`

## 出力フォーマット

```markdown
## プロジェクト概要

**名前**: {project_name}
**言語/フレームワーク**: {detected_stack}
**説明**: {description_from_readme}

## ディレクトリ構造

{tree_output}

## 主要コンポーネント

| ディレクトリ | 役割 | 主なファイル |
|-------------|------|-------------|
| src/        | メインソースコード | ... |
| tests/      | テストコード | ... |

## 開発環境

- **パッケージマネージャー**: {npm/yarn/pnpm/cargo/pip}
- **ビルドコマンド**: {build_command}
- **テストコマンド**: {test_command}

## 次のステップ

- [ ] {recommendation_1}
- [ ] {recommendation_2}
```

## 注意事項

- `node_modules/`, `.git/`, `vendor/`, `dist/`, `build/` は探索対象外
- 大規模プロジェクトでは深さ2-3レベルまでに制限
- 機密情報を含む可能性のあるファイル（`.env`等）の内容は表示しない
