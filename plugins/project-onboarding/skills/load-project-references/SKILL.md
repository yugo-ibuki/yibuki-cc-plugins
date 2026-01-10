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

## 参照ファイルの検索

以下の場所を順に検索:

1. `.claude/PROJECT_REFERENCES.md`
2. `PROJECT_REFERENCES.md`（プロジェクトルート）
3. `docs/PROJECT_REFERENCES.md`
4. `.claude/GLOSSARY.md`
5. `GLOSSARY.md`

```bash
# 検索パターン
find . -maxdepth 3 \( -name "PROJECT_REFERENCES.md" -o -name "GLOSSARY.md" \) 2>/dev/null
```

## 期待されるフォーマット

### PROJECT_REFERENCES.md の構造

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

## 略語・別名

| 略語 | 正式名称 | 備考 |
|------|---------|------|
| WS | Workspace | 内部での省略形 |
| Repo | Repository | コード内での命名 |
```

## 出力

読み込んだ情報を構造化して返却:

```json
{
  "domain_terms": [
    {
      "term": "ワークスペース",
      "description": "ユーザーの作業領域",
      "related_paths": ["src/workspace/", "models/Workspace.ts"]
    }
  ],
  "technical_terms": [...],
  "directories": [...],
  "aliases": {
    "WS": "Workspace",
    "Repo": "Repository"
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
