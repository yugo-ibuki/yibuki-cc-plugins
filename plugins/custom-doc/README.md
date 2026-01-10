# custom-doc-plugin

カスタムドキュメントの作成・更新・検索・コンテキスト共有を行うプラグイン

## コマンド一覧

| コマンド | 説明 |
|----------|------|
| `/create-doc` | カスタムドキュメントを新規作成 |
| `/update-doc` | 既存ドキュメントに変更を追記 |
| `/create-investigate-doc` | コードベース調査レポートを作成 |
| `/update-investigate-doc` | 既存の調査ドキュメントを更新 |

## 使用方法

### ドキュメント作成

```bash
# セッションの内容をドキュメント化
/create-doc

# 名前を指定して作成
/create-doc feature-auth-login

# コードベース調査レポートを作成
/create-investigate-doc auth-system
```

### ドキュメント更新

```bash
# 既存ドキュメントに変更を追記
/update-doc

# キーワードで絞り込んで更新
/update-doc auth

# 調査ドキュメントを更新
/update-investigate-doc auth-system-investigation
```

## ドキュメント保存先

```
.claude/custom-documents/
├── feature-auth-login/
│   ├── document.md
│   └── document.html
├── api-refactor/
│   └── ...
└── ...
```

## HTML生成

マークダウンからHTMLを生成:

```bash
python plugins/custom-doc/scripts/markdown-to-html.py .claude/custom-documents/<ディレクトリ名>/
```

## ファイル構成

```
plugins/custom-doc/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── create-doc.md
│   ├── create-investigate-doc.md
│   ├── update-doc.md
│   └── update-investigate-doc.md
├── scripts/
│   ├── markdown-to-html.py
│   └── select-doc.py
├── skills/
│   ├── search-related-docs.md  # 関連ドキュメント検索スキル
│   ├── load-doc-context.md     # コンテキスト読み込みスキル
│   ├── doc-to-html.md
│   ├── example-doc.md
│   ├── example-doc.html
│   └── README.md
└── README.md
```

## スキル（内部機能）

コマンド実行時に自動で使用される内部スキル：

### search-related-docs

関連するドキュメントを検索・特定するスキル。

- `git status` の変更ファイルと既存ドキュメントを照合
- 関連度をスコアリング（ファイル一致、ディレクトリ一致、キーワード一致）
- 高関連度のドキュメントを候補として提示

### load-doc-context

ドキュメントを読み込んでコンテキストとして取り込むスキル。

- ドキュメント内容を構造化して解析
- 記載済みファイル一覧を抽出
- コンテキストサマリーを生成

## worktree間のコンテキスト共有

このプラグインは、複数のworktreeで並列作業する際のコンテキスト共有を支援します:

1. **作業開始時**: コマンド実行時に関連ドキュメントを自動検索（search-related-docs スキル）
2. **関連発見時**: 既存ドキュメントをコンテキストとして読み込み（load-doc-context スキル）
3. **作業完了時**: `/create-doc` または `/update-doc` で知見を記録
4. **別worktreeで**: 同じドキュメントが自動的に検索・参照される
