---
name: search-related-docs
description: Search and identify related documents to complement context during command execution
version: 1.0.0
author: yugo-ibuki
keywords:
  - search
  - related
  - context
  - documents
  - git
  - worktree
used-by:
  - /create-doc
  - /update-doc
  - /create-investigate-doc
  - /update-investigate-doc
dependencies:
  - git (for file change detection)
  - .claude/custom-documents directory
---

# search-related-docs スキル

コマンド実行時に関連するドキュメントを検索し、コンテキストを補完するための内部スキル。

## 目的

`/create-doc` や `/update-doc` 実行時に：
1. 現在の作業に関連するドキュメントを自動検索
2. 関連度の高いドキュメントを提示
3. 必要に応じてユーザーに確認を求める

## 検索ロジック

### 検索対象
```
.claude/custom-documents/
├── feature-auth-login/
├── api-refactor/
└── ...
```

### 関連度判定の基準

| 判定要素 | 重み | 説明 |
|----------|------|------|
| 変更ファイルの一致 | 高 | 同じファイルを過去に変更したドキュメント |
| ディレクトリの一致 | 高 | 同じディレクトリ配下のファイルを扱うドキュメント |
| キーワードの一致 | 中 | 概要や実装内容に同じキーワードが含まれる |
| 技術スタックの一致 | 中 | 同じ技術やライブラリを使用 |
| 時間的近接性 | 低 | 最近更新されたドキュメント |

### 検索フロー

```
1. git status/diff から現在の変更ファイル一覧を取得
2. 各ドキュメントの「変更したファイル」セクションと照合
3. 関連度スコアを計算
4. スコアの高い順にソート
5. 閾値以上のドキュメントを候補として返す
```

## 使用方法（コマンド内での呼び出し）

### 基本的な検索

```markdown
## 関連ドキュメント検索

以下の手順で関連ドキュメントを検索：

1. `.claude/custom-documents/` 内の全ディレクトリを走査
2. 各ドキュメントの内容を解析
3. 現在の変更ファイルとの関連度を計算
4. 関連度の高いドキュメントをリストアップ
```

### 検索結果の提示形式

```markdown
📚 関連する可能性のあるドキュメントが見つかりました：

1. **feature-auth-login** (関連度: 高)
   - 一致: `src/auth/login.ts`, `src/auth/middleware.ts`
   - 概要: ログイン機能の実装

2. **api-auth-system** (関連度: 中)
   - 一致: `src/auth/` ディレクトリ
   - 概要: 認証APIの設計

これらのドキュメントを参照しますか？
- (y) はい、コンテキストとして読み込む
- (n) いいえ、新規ドキュメントとして作成
- (1-2) 特定のドキュメントのみ選択
```

## コマンドへの組み込み例

### create-doc での使用

```markdown
## ドキュメント作成前の確認

ドキュメント作成前に `skills/search-related-docs.md` を参照し：

1. 関連ドキュメントを検索
2. 高関連度のドキュメントがあれば確認を求める
3. ユーザーの選択に応じて：
   - 既存ドキュメントを更新 → /update-doc にリダイレクト
   - 新規作成を継続
   - 既存ドキュメントをコンテキストとして参照しながら新規作成
```

### update-doc での使用

```markdown
## 更新対象の特定

`skills/search-related-docs.md` を使用して：

1. 現在の変更に最も関連するドキュメントを特定
2. 複数候補がある場合は選択を求める
3. 関連度が低い場合は警告を表示
```

## 出力フォーマット

### 検索結果オブジェクト（内部用）

```yaml
results:
  - name: "feature-auth-login"
    path: ".claude/custom-documents/feature-auth-login/"
    relevance: high
    matched_files:
      - "src/auth/login.ts"
      - "src/auth/middleware.ts"
    summary: "ログイン機能の実装"
    last_updated: "2024-11-20"

  - name: "api-auth-system"
    path: ".claude/custom-documents/api-auth-system/"
    relevance: medium
    matched_files: []
    matched_directory: "src/auth/"
    summary: "認証APIの設計"
    last_updated: "2024-11-15"
```

## 注意事項

- 検索はMarkdownファイルのみを対象
- 大文字小文字は区別しない
- 部分一致で検索（完全一致は不要）
- 検索結果が多すぎる場合は上位5件に制限
