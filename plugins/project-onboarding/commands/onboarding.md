---
allowed-tools:
  - Task
description: プロジェクト構造を探索し、新規参加者向けの概要を提供（subagent実行）
argument-hint:
---

# /onboarding コマンド

プロジェクトに新しく参加したメンバーがプロジェクト全体を把握するためのコマンドです。

## 実行方法

このコマンドは `project-onboarding` subagentを起動し、プロジェクト探索を実行します。
コンテキストを節約するため、詳細な検索処理はsubagent内で完結します。

## Taskツールでの呼び出し

```
Task tool:
  subagent_type: "project-onboarding"
  description: "プロジェクト概要を取得"
  prompt: |
    このプロジェクトの概要を把握して、新規参加者向けにまとめてください。

    以下を調査:
    1. README.md, CLAUDE.md からプロジェクト説明を取得
    2. package.json 等から技術スタックを特定
    3. ディレクトリ構造を探索
    4. PROJECT_REFERENCES.md があれば用語集を取得

    結果を以下のフォーマットで出力:
    - プロジェクト名・説明
    - 技術スタック
    - ディレクトリ構造と各ディレクトリの役割
    - プロジェクト固有の用語（あれば）
```

## 出力フォーマット

subagentから返される結果:

```markdown
# プロジェクトオンボーディング

## 基本情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | {name} |
| 説明 | {description} |
| 技術スタック | TypeScript, React, Node.js |

## ディレクトリ構造

src/
├── components/    # UIコンポーネント
├── services/      # ビジネスロジック
└── utils/         # ユーティリティ

## 次のステップ

- `/find-files <タスク名>` で関連ファイルを探す
```

## メリット

- **コンテキスト節約**: 検索処理の詳細がメインコンテキストに残らない
- **高速**: 並列検索が可能
- **再利用性**: 同じagentを `/find-files` でも使用
