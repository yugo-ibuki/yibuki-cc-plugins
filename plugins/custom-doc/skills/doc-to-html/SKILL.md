---
name: doc-to-html
description: マークダウンドキュメントをフローティング目次・コピー機能・トグルセクション付きの読みやすいHTMLに変換するスキル。/create-doc, /update-doc, /create-investigate-doc, /update-investigate-doc の後処理として使用。python3 と scripts/markdown-to-html.py が必要。
allowed-tools:
  - Read
  - Write
  - Bash(python3:*)
user-invocable: true
---

# ドキュメントHTML化スキル

マークダウン形式のドキュメントを、目次・コピー機能・トグル展開機能を備えた読みやすいHTMLに変換します。

## 機能

### 1. フローティング目次
- 左側に固定配置
- スクロールに追随
- クリックで該当セクションにジャンプ
- 現在位置のハイライト

### 2. ファイルパス表示
- コードブロックにファイルパスを表示
- クリックでパスをクリップボードにコピー
- コピー成功時の視覚フィードバック

### 3. 重要度別トグル
- 詳細情報は折りたたみ可能
- 概要・実装内容は常時表示
- 技術的背景・参考資料は展開式

### 4. デザイン
- 落ち着いた色合い（ダークグレー基調）
- 読みやすいフォントサイズと行間
- 適切なコントラスト比
- レスポンシブ対応

## 使用方法

```bash
# マークダウンファイルを指定してHTML化
/doc-to-html path/to/document.md

# ディレクトリ内の全ドキュメントをHTML化
/doc-to-html path/to/directory/
```

## 生成されるHTML構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[ドキュメント名]</title>
    <style>
        /* スタイルシート */
    </style>
</head>
<body>
    <nav class="toc">
        <!-- 目次 -->
    </nav>
    <main class="content">
        <!-- メインコンテンツ -->
    </main>
    <script>
        /* インタラクション用スクリプト */
    </script>
</body>
</html>
```

## マークダウンからHTMLへの変換ルール

### 常時表示セクション
- 概要
- 変更したファイル
- 実装内容

### トグル展開セクション（デフォルト折りたたみ）
- 技術的な背景・解説
- 技術的な判断・設計決定
- セキュリティ観点
- 注意点・制約
- 関連知識・参考資料

## 出力先

生成されたHTMLは元のマークダウンファイルと同じディレクトリに `[filename].html` として保存されます。

例：
- `task-implementation.md` → `task-implementation.html`

## CSS変数

```css
:root {
    --bg-primary: #1e1e1e;
    --bg-secondary: #252526;
    --bg-tertiary: #2d2d30;
    --text-primary: #d4d4d4;
    --text-secondary: #9e9e9e;
    --accent: #569cd6;
    --accent-hover: #4a8bc2;
    --border: #3e3e42;
    --code-bg: #1e1e1e;
    --success: #4ec9b0;
}
```

## JavaScript機能

- 目次のアクティブ状態更新（スクロール追随）
- スムーススクロールナビゲーション
- ファイルパスのクリップボードコピー
- トグルセクションの展開・折りたたみ
- モバイルメニュー対応

## カスタマイズ

HTMLのデザインやスタイルをカスタマイズしたい場合は、以下のファイルを編集してください：

- `scripts/markdown-to-html.py` - HTMLテンプレートとCSS定義
- `skills/doc-to-html/SKILL.md` - スキルのドキュメント
