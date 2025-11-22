---
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
  - Bash(git add *)
  - Bash(git status *)
  - Bash(git diff *)
  - Bash(python3 *)
description: 既存のカスタムドキュメントを更新
argument-hint: <ディレクトリ名>
---

## 実行内容

`.claude/custom-document` 内の既存ドキュメントに、現在のセッションでの変更内容を追記します。

## 使用方法

```bash
/update-doc              # 引数なし：候補を表示して選択
/update-doc auth         # キーワード絞り込み："auth"を含むドキュメントを検索
/update-doc feature-auth # 完全一致：直接指定
```

## 絞り込み動作

### パターン1: 引数なし
```bash
/update-doc
```
1. `.claude/custom-document/` 内の全ドキュメントをリスト表示
   ```
   以下のドキュメントが見つかりました：
   1. feature-auth-login
   2. feature-auth-signup
   3. api-auth-system
   4. refactor-database

   番号を入力してください、またはキーワードで絞り込めます
   ```
2. 番号で選択 or キーワード入力で絞り込み
3. ユーザーの応答を待つ（会話的な選択）

### パターン2: キーワード指定
```bash
/update-doc auth
```
1. "auth"を含むドキュメントを検索（部分一致）
2. **1件のみヒット** → 自動選択して確認
3. **複数ヒット** → リスト表示して会話的に選択
4. **ヒットなし** → 全ドキュメントを表示

### パターン3: 完全一致
```bash
/update-doc feature-auth-system
```
1. 完全一致するディレクトリがあれば自動選択
2. なければパターン2の部分一致で検索

## 選択方式

**ヘルパースクリプトを使用:**
- `scripts/select-doc.py` を使ってインタラクティブに選択
- 候補が複数ある場合、番号付きリストで表示
- ユーザーの応答を待って、番号またはキーワードを受け付ける
- 候補数に制限なし（大量のドキュメントにも対応）

### スクリプトの使い方
```bash
# 全ドキュメントから選択
python3 .claude-plugin/scripts/select-doc.py

# キーワードで絞り込んでから選択
python3 .claude-plugin/scripts/select-doc.py auth

# コマンド内での利用例
SELECTED=$(python3 .claude-plugin/scripts/select-doc.py "$ARGUMENT")
echo "選択: $SELECTED"
```

選択されたディレクトリ名が標準出力に出力されるので、それを使ってドキュメントを更新します。

## 自動的に追加される内容

### 1. 変更したファイル
`git status` と `git diff` から変更ファイルを検出し、追記します。

### 2. 実装内容
このセッションでの会話と変更内容から、実装した内容を抽出して追加します。

### 3. 技術的な背景・解説
必要に応じて、新しい技術トピックを追加します。

### 4. 関連知識・参考資料
参照した公式ドキュメントや記事があれば追加します。

## 動作

1. 指定されたディレクトリを `.claude/custom-document/` 内で検索
2. 既存ドキュメントを読み込み
3. セッション内容を解析
4. 各セクションに新しい情報を追記（タイムスタンプ付き）
5. 差分を表示して確認

## 更新例

**Before:**
```markdown
## 変更したファイル
- `src/auth/login.ts` - ログイン機能の実装

## 実装内容
### ログイン機能
- JWT認証の実装
```

**After:**
```markdown
## 変更したファイル
- `src/auth/login.ts` - ログイン機能の実装
- `src/auth/logout.ts` - ログアウト機能の追加（2024-11-22）

## 実装内容
### ログイン機能
- JWT認証の実装

### ログアウト機能（2024-11-22追加）
- トークン無効化の実装
- セッション削除処理
```

## 注意点

- 既存内容は保持され、新しい内容が追記されます
- タイムスタンプ `(YYYY-MM-DD追加)` が自動的に付きます
- 重複内容は自動的にスキップされます
