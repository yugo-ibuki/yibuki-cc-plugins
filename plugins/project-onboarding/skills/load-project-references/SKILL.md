---
name: load-project-references
description: PROJECT_REFERENCES.mdを読み込み、プロジェクト固有の用語、ディレクトリ、ファイルのマッピング情報を取得する。関連ファイル検索の精度向上のために自動的に呼び出される。
version: "1.0.0"
allowed-tools:
  - Read
  - Glob
  - Grep
---

# load-project-references スキル

プロジェクト固有の用語集（PROJECT_REFERENCES.md）を読み込み、検索の精度を向上させます。

## 優先読み込みファイル

### プロジェクト用語集
1. `.claude/PROJECT_REFERENCES.md`（推奨）
2. `PROJECT_REFERENCES.md`（プロジェクトルート）
3. `docs/PROJECT_REFERENCES.md`
4. `.claude/GLOSSARY.md`
5. `GLOSSARY.md`
6. `.local.env`（環境変数のキー名から用語を推測）

### プロジェクト情報
- `README.md` / `README.*` - プロジェクト概要
- `CLAUDE.md` - Claude Code用の指示
- `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` - 依存関係・プロジェクト情報
- `.env.example` / `.env.sample` - 環境変数
- `Makefile` / `Dockerfile` / `docker-compose.yml` - ビルド・実行環境

```bash
# 検索パターン
find . -maxdepth 3 \( -name "PROJECT_REFERENCES.md" -o -name "GLOSSARY.md" -o -name ".local.env" \) 2>/dev/null
```

## 期待されるフォーマット

### PROJECT_REFERENCES.md の構造

**セクション名は柔軟にカスタマイズ可能です。** `##` で始まる見出しを自動検出し、配下のMarkdownテーブルを解析します。

```markdown
# プロジェクト用語集

## ドメイン用語

| 用語 | 説明 | 関連ファイル/ディレクトリ |
|------|------|-------------------------|
| ワークスペース | ユーザーの作業領域 | `src/workspace/`, `models/Workspace.ts` |
| タスク | 実行可能な作業単位 | `src/tasks/`, `models/Task.ts` |

## 技術用語

| 用語 | 説明 | 関連ファイル/ディレクトリ |
|------|------|-------------------------|
| Repository | データ永続化層 | `src/repositories/` |
| UseCase | ビジネスロジック層 | `src/usecases/` |

## ディレクトリ構成

| ディレクトリ | 役割 | 主要ファイル |
|-------------|------|-------------|
| src/domain/ | ドメインモデル | Entity, ValueObject |
| src/infra/ | インフラ層 | DB接続, 外部API |
```

### フォーマット柔軟性

- **セクション名**: 任意（`## ビジネス概念`, `## アーキテクチャ用語` など）
- **カラム名**: 最初のヘッダー行から自動検出
- **カラム数**: 可変（2列でも5列でも対応）

例:

```markdown
## ビジネス概念

| 概念 | 定義 | 実装場所 | 備考 |
|------|------|---------|------|
| 契約 | 顧客との契約情報 | `src/contracts/` | ... |

## モジュール構成

| モジュール | 責務 |
|-----------|------|
| auth | 認証・認可 |
```

## 解析ロジック

1. `##` で始まる行をセクションとして検出
2. 各セクション配下のMarkdownテーブル（`|` で区切られた行）を抽出
3. ヘッダー行（最初のテーブル行）からカラム名を取得
4. データ行を構造化データとして格納

## 出力

読み込んだ情報を構造化して返却（セクション名をキーとした動的構造）:

```json
{
  "sections": {
    "ドメイン用語": {
      "headers": ["用語", "説明", "関連ファイル/ディレクトリ"],
      "rows": [
        ["ワークスペース", "ユーザーの作業領域", "src/workspace/, models/Workspace.ts"],
        ["タスク", "実行可能な作業単位", "src/tasks/, models/Task.ts"]
      ]
    },
    "技術用語": {
      "headers": ["用語", "説明", "関連ファイル/ディレクトリ"],
      "rows": [...]
    }
  }
}
```

## 参照ファイルがない場合

参照ファイルが存在しない場合は、以下を提案:

```markdown
## PROJECT_REFERENCES.md の作成を推奨

プロジェクト固有の用語やディレクトリ構成を記録することで、
新規参加者のオンボーディングや関連ファイル検索の精度が向上します。

### 作成手順

1. `.claude/PROJECT_REFERENCES.md` を作成
2. 上記のテンプレートに従って用語を記載
3. 定期的にメンテナンス

### テンプレートの生成

`/create-project-references` コマンドで自動生成できます。
```

## 注意事項

- 機密情報（APIキー、パスワード等）は参照ファイルに含めない
- 用語は一意に特定できるよう、十分な説明を記載
- ディレクトリパスは相対パスで記載
