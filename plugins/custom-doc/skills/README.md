# Custom Document Skills

カスタムドキュメントプラグインのスキル定義ディレクトリ

## ディレクトリ構造

```
skills/
├── README.md
├── search-related-docs/
│   └── SKILL.md
├── load-doc-context/
│   └── SKILL.md
├── doc-to-html/
│   └── SKILL.md
├── example-doc.md
└── example-doc.html
```

## スキル一覧

### search-related-docs（内部スキル）

コマンド実行時に関連ドキュメントを検索・特定するスキル。

**使用コマンド:** `/create-doc`, `/update-doc`, `/create-investigate-doc`, `/update-investigate-doc`

**機能:**
- `git status` の変更ファイルと既存ドキュメントを照合
- 関連度スコアリング（ファイル一致、ディレクトリ一致、キーワード一致）
- 高関連度のドキュメントを候補として提示
- ユーザーに確認を求める

### load-doc-context（内部スキル）

ドキュメントを読み込んでコンテキストとして取り込むスキル。

**使用コマンド:** `/create-doc`, `/update-doc`, `/create-investigate-doc`, `/update-investigate-doc`

**機能:**
- ドキュメント内容を構造化して解析
- 記載済みファイル一覧を抽出
- コンテキストサマリーを生成
- 差分検出（update-doc, update-investigate-doc 用）

---

### doc-to-html（ユーザー呼び出し可能）

マークダウンドキュメントを読みやすいHTMLに変換するスキル

**機能:**
- フローティング目次（スクロール追随）
- ファイルパスのワンクリックコピー
- 詳細セクションのトグル展開
- 落ち着いた色合いのダークモードデザイン
- レスポンシブ対応

**使用方法:**

```bash
# 単一ファイルを変換
python plugins/custom-doc/scripts/markdown-to-html.py path/to/document.md

# ディレクトリ内の全マークダウンを変換
python plugins/custom-doc/scripts/markdown-to-html.py path/to/directory/
```

**生成されるHTML:**

- 左側にフローティング目次
- メインコンテンツエリアは十分な幅を確保
- コードブロックにはファイルパス表示とコピーボタン
- 技術的詳細は折りたたみ可能
- ダークグレー基調の落ち着いたデザイン

## サンプル

`example-doc.md` と `example-doc.html` がサンプルとして用意されています。

HTMLをブラウザで開いて機能を確認できます：

```bash
open plugins/custom-doc/skills/example-doc.html
```

## スキルの追加方法

新しいスキルを追加する場合は、ディレクトリを作成して `SKILL.md` ファイルを配置してください：

```
skills/
└── new-skill-name/
    └── SKILL.md
```

SKILL.md のフォーマット：

```markdown
---
name: skill-name
description: スキルの説明（自動呼び出しのマッチングに使用）
allowed-tools:
  - Read
  - Write
  - Bash(specific:*)
user-invocable: false  # ユーザーが直接呼び出せる場合は true
---

# スキル名

スキルの詳細な説明...
```

## 公式フロントマターフィールド

| フィールド | 説明 |
|------------|------|
| name | スキル名 |
| description | 説明（自動呼び出しのマッチングに使用） |
| allowed-tools | スキルが使用できるツール |
| model | 使用するモデル（オプション） |
| context | 含めるコンテキストファイル（オプション） |
| agent | エージェント設定（オプション） |
| hooks | 実行前後のフック（オプション） |
| user-invocable | ユーザーが直接呼び出せるか（デフォルト: false） |
| disable-model-invocation | モデルによる自動呼び出しを無効化（オプション） |
