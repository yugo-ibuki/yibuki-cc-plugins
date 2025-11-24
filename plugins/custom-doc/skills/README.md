# Custom Document Skills

カスタムドキュメントプラグインのスキル定義ディレクトリ

## スキル一覧

### doc-to-html

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

## カスタマイズ

HTMLのデザインやスタイルをカスタマイズしたい場合は、以下のファイルを編集してください：

- `scripts/markdown-to-html.py` - HTMLテンプレートとCSS定義
- `skills/doc-to-html.md` - スキルのドキュメント

## スキル定義の追加

新しいスキルを追加する場合は、このディレクトリに `.md` ファイルを作成してください。

```markdown
---
name: skill-name
description: スキルの説明
---

# スキル名

スキルの詳細な説明...
```
