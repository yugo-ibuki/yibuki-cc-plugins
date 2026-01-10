---
allowed-tools:
  - Task
description: タスクやキーワードに関連するファイルを検索して説明（subagent実行）
argument-hint: <キーワードまたはタスク名>
---

# /find-files コマンド

タスクやキーワードに基づいて関連するファイルやディレクトリを検索し、
その役割と関連性を説明します。

## 実行方法

このコマンドは `project-onboarding` subagentを起動し、ファイル検索を実行します。
コンテキストを節約するため、詳細な検索処理はsubagent内で完結します。

## 使用例

```bash
/find-files ログイン          # 「ログイン」に関連するファイルを検索
/find-files 認証 API          # 複数キーワードで検索
/find-files UserService       # クラス名やモジュール名で検索
/find-files 決済処理          # 機能名で検索
```

## Taskツールでの呼び出し

```
Task tool:
  subagent_type: "project-onboarding"
  description: "関連ファイル検索: {keyword}"
  prompt: |
    「{keyword}」に関連するファイルを検索してください。

    実行内容:
    1. PROJECT_REFERENCES.md があれば用語マッピングを取得
    2. キーワードを展開（日本語→英語、ケース変換）
    3. ファイル名・ディレクトリ名で検索
    4. ファイル内容で grep 検索
    5. 主要ファイルのimport解析
    6. 逆参照（どこから呼ばれているか）を検索
    7. monorepo構成があれば、どのパッケージから使われているか

    出力フォーマット:
    - 直接関連ファイル（★★★）
    - 関連ディレクトリ
    - 依存関係（imports/imported by）
    - monorepoパッケージマップ（該当する場合）
    - 推奨アクション
```

## 出力フォーマット

subagentから返される結果:

```markdown
# 検索結果: "{keyword}"

## 直接関連ファイル

| ファイル | 説明 | 関連度 |
|---------|------|--------|
| `src/auth/login.ts` | ログイン処理の実装 | ★★★ |
| `src/components/LoginForm.tsx` | ログインフォームUI | ★★★ |

## 関連ディレクトリ

| ディレクトリ | 役割 | ファイル数 |
|-------------|------|-----------|
| `src/auth/` | 認証関連ロジック | 8 |

## 依存関係（Dependencies）

このファイルがimportしているもの:
| モジュール | 種別 |
|-----------|------|
| `./utils/validation` | 内部 |
| `@myorg/shared` | monorepoパッケージ |

## 逆参照（Dependents）

**同一パッケージ内:**
- `src/pages/LoginPage.tsx`
- `src/hooks/useAuth.ts`

**他パッケージから（monorepo）:**
| パッケージ | ファイル |
|-----------|---------|
| `apps/web` | `src/auth/index.ts` |
| `apps/admin` | `src/lib/auth.ts` |

## 依存関係ツリー

```
LoginPage.tsx
├── imports: LoginForm.tsx, useAuth.ts
└── imported by: [apps/web] App.tsx
```

## monorepo パッケージマップ

| パッケージ | 関係 | 参照数 |
|-----------|------|-------|
| @myorg/web | 使用元 | 3 |
| @myorg/admin | 使用元 | 1 |

## 推奨アクション

- まず `src/auth/login.ts` を確認してください
- **monorepo注意**: 複数パッケージに影響があります
```

## メリット

- **コンテキスト節約**: 検索処理の詳細がメインコンテキストに残らない
- **高速**: 並列検索が可能
- **import解析**: 依存関係と逆参照を自動分析
- **monorepo対応**: パッケージ間の依存を可視化
