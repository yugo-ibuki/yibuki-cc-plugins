---
allowed-tools:
  - Task
  - Read
  - Glob
  - Grep
  - Bash(ls:*)
  - Bash(find:*)
description: タスクやキーワードに関連するファイルを検索して説明
argument-hint: <キーワードまたはタスク名>
---

# /find-files コマンド

タスクやキーワードに基づいて関連するファイルやディレクトリを検索し、
その役割と関連性を説明します。

## 使用例

```bash
/find-files ログイン          # 「ログイン」に関連するファイルを検索
/find-files 認証 API          # 複数キーワードで検索
/find-files UserService       # クラス名やモジュール名で検索
/find-files 決済処理          # 機能名で検索
```

## 実行方法

このコマンドは `Explore` agentを使用してファイル検索を実行します。
コンテキストを節約するため、詳細な検索処理はsubagent内で完結します。

## Taskツールでの呼び出し

```
Task tool:
  subagent_type: "Explore"
  description: "関連ファイル検索: {keyword}"
  prompt: |
    「{keyword}」に関連するファイルを検索してください。

    実行内容（thoroughness: "very thorough"）:
    1. PROJECT_REFERENCES.md があれば用語マッピングを取得
    2. キーワードを展開（日本語→英語、ケース変換: login, Login, LOGIN）
    3. ファイル名・ディレクトリ名で検索（Glob）
    4. ファイル内容で検索（Grep）
    5. 主要ファイルのimport文を解析
    6. 逆参照（どこからimportされているか）を検索

    出力フォーマット:

    ## 検索結果: "{keyword}"

    ### 直接関連ファイル（★★★）

    | ファイル | 説明 | 関連度 |
    |---------|------|--------|
    | `src/auth/login.ts` | ログイン処理の実装 | ★★★ |

    ### 関連ディレクトリ

    | ディレクトリ | 役割 |
    |-------------|------|
    | `src/auth/` | 認証関連ロジック |

    ### 依存関係

    **このファイルがimportしているもの:**
    - `./utils/validation`
    - `axios`

    **このファイルをimportしているもの:**
    - `src/pages/LoginPage.tsx`
    - `src/hooks/useAuth.ts`

    ### 推奨アクション

    - まず `src/auth/login.ts` を確認してください
```

## 検索除外パターン

以下は自動的に除外されます:
- `node_modules/`
- `.git/`
- `dist/`, `build/`, `.next/`
- `*.min.js`, `*.map`
- `coverage/`

## メリット

- **コンテキスト節約**: 検索処理の詳細がメインコンテキストに残らない
- **高速**: Explore agentによる効率的な検索
- **import解析**: 依存関係と逆参照を自動分析
