---
allowed-tools:
  - Task
  - Read
  - Glob
  - Grep
  - Bash(ls:*)
description: プロジェクト構造を探索し、新規参加者向けの概要を提供
argument-hint:
---

# /onboarding コマンド

プロジェクトに新しく参加したメンバーがプロジェクト全体を把握するためのコマンドです。

## 実行方法

このコマンドは `Explore` agentを使用してプロジェクト構造を探索します。
コンテキストを節約するため、詳細な検索処理はsubagent内で完結します。

## Taskツールでの呼び出し

```
Task tool:
  subagent_type: "Explore"
  description: "プロジェクト概要を取得"
  prompt: |
    このプロジェクトの概要を把握して、新規参加者向けにまとめてください。

    以下を調査（thoroughness: "very thorough"）:
    1. README.md, CLAUDE.md からプロジェクト説明を取得
    2. package.json, pyproject.toml, Cargo.toml 等から技術スタックを特定
    3. ディレクトリ構造を探索（src/, lib/, app/ 等）
    4. PROJECT_REFERENCES.md があれば用語集を取得

    結果を以下のフォーマットで出力:

    ## プロジェクト概要

    | 項目 | 内容 |
    |------|------|
    | プロジェクト名 | {name} |
    | 説明 | {description} |
    | 技術スタック | {technologies} |

    ## ディレクトリ構造

    ```
    src/
    ├── components/    # 役割説明
    ├── services/      # 役割説明
    └── utils/         # 役割説明
    ```

    ## 主要ファイル

    - `{path}` - {説明}

    ## プロジェクト固有の用語（あれば）

    | 用語 | 意味 |
    |------|------|

    ## 次のステップ

    - `/find-files <キーワード>` で関連ファイルを探す
```

## メリット

- **コンテキスト節約**: 検索処理の詳細がメインコンテキストに残らない
- **高速**: Explore agentによる効率的な探索
- **再利用性**: 同じパターンを `/find-files` でも使用
