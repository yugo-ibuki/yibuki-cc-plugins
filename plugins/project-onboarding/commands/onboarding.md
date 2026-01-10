---
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(ls:*)
  - Bash(tree:*)
  - Bash(find:*)
  - Bash(wc:*)
  - Bash(cat:*)
  - Bash(git log:*)
  - Bash(git branch:*)
description: プロジェクト構造を探索し、新規参加者向けの概要を提供
argument-hint:
---

# /onboarding コマンド

プロジェクトに新しく参加したメンバーがプロジェクト全体を把握するためのコマンドです。

## 参照スキル

- `skills/explore-project/SKILL.md` - プロジェクト構造の探索
- `skills/load-project-references/SKILL.md` - プロジェクト用語集の読み込み

## 実行フロー

### Step 1: プロジェクト設定ファイルの確認

以下のファイルを優先的に読み込み、プロジェクトの基本情報を取得:

1. `README.md` - プロジェクト概要
2. `CLAUDE.md` - 開発ガイドライン
3. `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` - プロジェクト設定
4. `.env.example` - 環境変数の例

### Step 2: ディレクトリ構造の把握

```bash
# トップレベル構造を取得（2階層まで）
tree -L 2 -d --noreport 2>/dev/null || find . -maxdepth 2 -type d | head -50

# 主要ディレクトリのファイル数を確認
find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | cut -d/ -f2 | sort | uniq -c | sort -rn | head -10
```

### Step 3: プロジェクト用語集の読み込み

`load-project-references` スキルを使用して、プロジェクト固有の用語を取得。

### Step 4: 技術スタックの検出

以下を自動検出:

- **言語**: TypeScript, JavaScript, Python, Go, Rust, Java など
- **フレームワーク**: React, Vue, Next.js, Django, FastAPI, Gin など
- **ビルドツール**: npm, yarn, pnpm, cargo, pip など
- **テストツール**: Jest, Vitest, pytest, go test など

### Step 5: Git情報の取得

```bash
# 最近のコミット履歴
git log --oneline -10

# 現在のブランチ
git branch --show-current

# リモートブランチ一覧
git branch -r
```

## 出力フォーマット

```markdown
# プロジェクトオンボーディング

## 基本情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | {name} |
| 説明 | {description} |
| 言語/フレームワーク | {stack} |
| パッケージマネージャー | {package_manager} |

## ディレクトリ構造

{tree_output}

### 主要ディレクトリの役割

| ディレクトリ | 役割 | 備考 |
|-------------|------|------|
| src/ | メインソースコード | ... |
| tests/ | テストコード | ... |
| docs/ | ドキュメント | ... |

## 開発を始めるには

### 環境構築

{setup_commands}

### よく使うコマンド

| コマンド | 説明 |
|---------|------|
| `{build_cmd}` | ビルド |
| `{test_cmd}` | テスト実行 |
| `{dev_cmd}` | 開発サーバー起動 |

## プロジェクト固有の用語

{project_references_table}

## 最近の開発状況

### 直近のコミット

{recent_commits}

### アクティブなブランチ

{active_branches}

## 次のステップ

- [ ] 環境構築を完了する
- [ ] READMEを読む
- [ ] 最初のタスクに取り組む - `/find-files <タスク名>` で関連ファイルを探す
```

## 注意事項

- `node_modules/`, `.git/`, `vendor/`, `dist/`, `build/` は探索対象外
- 機密情報（`.env`の内容等）は表示しない
- 大規模プロジェクトでは探索深度を制限
