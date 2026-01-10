---
name: find-related-files
description: タスクやキーワードに関連するファイルやディレクトリを検索し、その役割と関連性を説明する。ユーザーが特定の機能やタスクに関連するコードを探す際に自動的に呼び出される。
version: "1.0.0"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(find:*)
  - Bash(wc:*)
---

# find-related-files スキル

タスクやキーワードに基づいて関連ファイルを検索し、その役割と関連性を説明します。

## 検索戦略

### 1. キーワード抽出

ユーザーの入力から以下を抽出:

- **機能名**: "ログイン", "認証", "決済" など
- **技術用語**: "API", "データベース", "キャッシュ" など
- **ファイル種別**: "コンポーネント", "サービス", "テスト" など

### 2. PROJECT_REFERENCES.md の参照

プロジェクトルートまたは `.claude/` に `PROJECT_REFERENCES.md` がある場合、
プロジェクト固有の用語とファイルのマッピングを読み込む。

```bash
# 参照ファイルの検索
find . -name "PROJECT_REFERENCES.md" -o -name "GLOSSARY.md" 2>/dev/null | head -5
```

### 3. 多角的検索

```bash
# ファイル名でのマッチング
find . -type f \( -name "*keyword*" -o -name "*Keyword*" \) 2>/dev/null

# ファイル内容での検索
grep -rl "keyword" --include="*.{ts,js,py,go,rs,java}" . 2>/dev/null

# ディレクトリ名でのマッチング
find . -type d -name "*keyword*" 2>/dev/null
```

### 4. 関連ファイルの特定

検索結果から以下を分析:

- **直接関連**: ファイル名やクラス名に含まれる
- **間接関連**: import/require で参照されている
- **テスト関連**: 対応するテストファイル

### 5. Import解析（analyze-imports スキルを使用）

見つかった主要ファイルに対して `analyze-imports` スキルを実行:

- **Dependencies（順方向）**: そのファイルがimportしているモジュール
- **Dependents（逆方向）**: そのファイルをimportしているファイル
- **monorepo解析**: どのパッケージ/アプリから呼ばれているか

```bash
# 逆参照の検索例
# src/services/authService.ts を参照しているファイル
grep -rl "authService\|from ['\"].*auth" --include="*.ts" --include="*.tsx" .

# monorepoパッケージからの参照
grep -rl "@myorg/auth\|from ['\"]@" apps/ packages/ --include="*.ts" 2>/dev/null
```

## 出力フォーマット

```markdown
## 検索結果: "{keyword}"

### 直接関連ファイル

| ファイル | 説明 | 関連度 |
|---------|------|--------|
| `src/auth/login.ts` | ログイン処理のメイン実装 | ★★★ |
| `src/components/LoginForm.tsx` | ログインフォームUI | ★★★ |

### 関連ディレクトリ

| ディレクトリ | 役割 |
|-------------|------|
| `src/auth/` | 認証関連の全ロジック |
| `src/api/auth/` | 認証APIエンドポイント |

### 関連テスト

- `tests/auth/login.test.ts`
- `tests/components/LoginForm.test.tsx`

### 依存関係（Dependencies）

このファイルがimportしているもの:
| モジュール | 種別 |
|-----------|------|
| `src/utils/validation.ts` | 内部モジュール |
| `src/services/api.ts` | 内部モジュール |
| `axios` | 外部パッケージ |

### 逆参照（Dependents）

このファイルをimportしているもの:

**同一パッケージ内:**
- `src/pages/LoginPage.tsx`
- `src/App.tsx`

**他パッケージから（monorepo）:**
| パッケージ | ファイル |
|-----------|---------|
| `apps/web` | `src/features/auth/index.ts` |
| `apps/admin` | `src/lib/auth.ts` |

### monorepo影響範囲

| パッケージ | 参照数 | 役割 |
|-----------|-------|------|
| @myorg/web | 3 | メインWebアプリ |
| @myorg/admin | 1 | 管理画面 |

### プロジェクト固有の用語（PROJECT_REFERENCESより）

| 用語 | 意味 | 関連ファイル |
|------|------|-------------|
| AuthContext | 認証状態の管理 | `src/contexts/AuthContext.tsx` |
```

## 検索のヒント

- 日本語と英語の両方で検索を試みる
- キャメルケース、スネークケース、ケバブケースのバリエーションを考慮
- 省略形や別名も検索対象に含める（auth ↔ authentication）
