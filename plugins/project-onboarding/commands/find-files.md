---
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(find:*)
  - Bash(wc:*)
description: タスクやキーワードに関連するファイルを検索して説明
argument-hint: <キーワードまたはタスク名>
---

# /find-files コマンド

タスクやキーワードに基づいて関連するファイルやディレクトリを検索し、
その役割と関連性を説明します。

## 参照スキル

- `skills/find-related-files/SKILL.md` - 関連ファイル検索
- `skills/load-project-references/SKILL.md` - プロジェクト用語集の読み込み

## 使用方法

```bash
/find-files ログイン          # 「ログイン」に関連するファイルを検索
/find-files 認証 API          # 複数キーワードで検索
/find-files UserService       # クラス名やモジュール名で検索
/find-files 決済処理          # 機能名で検索
```

## 実行フロー

### Step 1: プロジェクト用語集の読み込み

`load-project-references` スキルを使用して、プロジェクト固有の用語とファイルマッピングを取得。

### Step 2: キーワードの展開

ユーザー入力のキーワードを以下の形式に展開:

- **英語変換**: "ログイン" → "login", "Login", "LOGIN"
- **ケース変換**: "userService" → "user_service", "user-service", "UserService"
- **略語展開**: PROJECT_REFERENCES.md の別名マッピングを使用
- **同義語**: "認証" → "auth", "authentication", "authorize"

### Step 3: 多角的検索

以下の観点から検索を実行:

```bash
# ファイル名検索
find . -type f \( -name "*keyword*" -o -name "*Keyword*" \) \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' 2>/dev/null

# ディレクトリ名検索
find . -type d -name "*keyword*" \
  -not -path '*/node_modules/*' 2>/dev/null

# ファイル内容検索
grep -rl "keyword" --include="*.ts" --include="*.js" --include="*.py" \
  --include="*.go" --include="*.rs" --include="*.java" . 2>/dev/null | head -20
```

### Step 4: 関連性の分析

検索結果を以下の基準でスコアリング:

- **★★★ 高関連**: ファイル名/クラス名に直接含まれる
- **★★☆ 中関連**: 関数名/変数名に含まれる
- **★☆☆ 低関連**: コメントやドキュメントに含まれる

### Step 5: 依存関係の調査

主要ファイルについて、import/require 関係を分析:

```bash
# TypeScript/JavaScript の import を検索
grep -h "^import\|^from\|require(" <file> 2>/dev/null

# Python の import を検索
grep -h "^import\|^from" <file> 2>/dev/null
```

## 出力フォーマット

```markdown
# 検索結果: "{keyword}"

## 直接関連ファイル

| ファイル | 説明 | 関連度 |
|---------|------|--------|
| `src/auth/login.ts:45` | ログイン処理の実装 | ★★★ |
| `src/components/LoginForm.tsx:12` | ログインフォームUI | ★★★ |

## 関連ディレクトリ

| ディレクトリ | 役割 | ファイル数 |
|-------------|------|-----------|
| `src/auth/` | 認証関連ロジック | 8 |
| `src/api/auth/` | 認証APIエンドポイント | 3 |

## 関連テスト

- `tests/auth/login.test.ts` - ログイン機能のテスト
- `tests/components/LoginForm.test.tsx` - UIコンポーネントテスト

## 依存関係図

```
LoginPage.tsx
  └── LoginForm.tsx
        └── useAuth.ts
              └── authService.ts
                    └── api.ts
```

## プロジェクト用語との関連（PROJECT_REFERENCESより）

| 用語 | 説明 | このファイルとの関係 |
|------|------|---------------------|
| AuthContext | 認証状態管理 | LoginFormで使用 |

## 推奨アクション

- まず `src/auth/login.ts` を確認してください（メイン実装）
- テストは `tests/auth/login.test.ts` を参照
- UIの変更は `src/components/LoginForm.tsx` から
```

## 注意事項

- 検索結果が多すぎる場合は上位20件に制限
- バイナリファイル、ビルド成果物は検索対象外
- 機密情報を含む可能性のあるファイル内容は表示しない
