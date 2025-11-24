# カスタムドキュメントHTML化機能の実装

## 概要

マークダウンドキュメントを読みやすいHTMLに変換する機能を実装しました。目次、コピー機能、トグル展開などの機能を備えた、技術ドキュメント専用のビューアーを提供します。

## 変更したファイル

- `plugins/custom-doc/skills/doc-to-html.md` - スキル定義とドキュメント
- `plugins/custom-doc/scripts/markdown-to-html.py` - HTML生成スクリプト
- `plugins/custom-doc/commands/create-doc.md` - コマンド定義の更新

## 実装内容

### フローティング目次機能

```javascript
plugins/custom-doc/scripts/markdown-to-html.py
// スクロール位置に応じて目次のアクティブ状態を更新
function updateActiveLink() {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });
}
```

- 左側固定配置で常時表示
- スクロールに追随してアクティブセクションをハイライト
- クリックで該当セクションにスムーズスクロール

### ファイルパスコピー機能

コードブロックに表示されるファイルパスをワンクリックでコピーできる機能を実装。コピー成功時には視覚的フィードバックを提供します。

### トグル展開機能

詳細情報を折りたたみ可能にすることで、ドキュメントの可読性を向上。概要は常時表示し、詳細は必要に応じて展開できます。

## 技術的な背景・解説

### マークダウンパース処理

正規表現を使用してマークダウン構文を解析し、HTMLに変換します。主な処理対象：

- 見出し（h1-h3）の抽出とID生成
- コードブロックの検出とシンタックスハイライト対応
- リスト、リンク、太字、斜体の変換
- インラインコードの処理

### CSSによるデザインシステム

CSS変数を使用した一貫性のあるデザインシステムを構築：

```css
plugins/custom-doc/scripts/markdown-to-html.py
:root {
    --bg-primary: #1e1e1e;
    --bg-secondary: #252526;
    --text-primary: #d4d4d4;
    --accent: #569cd6;
}
```

ダークモードベースで目に優しい配色を採用し、コードエディタ風の落ち着いた雰囲気を実現しています。

## 技術的な判断・設計決定

**なぜPythonスクリプトを選択したか**

- マークダウンパース処理の柔軟性
- 正規表現による高度なパターンマッチング
- ファイルI/O処理の簡潔さ
- プロジェクト内の他のスクリプトとの一貫性

**トレードオフの考慮**

- シンプルさを優先し、外部ライブラリ（markdown2, mistune等）は使用しない
- 複雑なマークダウン構文（テーブル、脚注等）は現時点ではサポート外
- 必要に応じて将来的に機能拡張可能な設計

## セキュリティ観点

### 対策済みの項目

- HTMLエスケープ処理による XSS 対策
- ユーザー入力の適切なサニタイゼーション
- ファイルパスの検証とパストラバーサル対策

### 検討が必要な項目

- 大容量マークダウンファイルの処理制限
- 外部リンクのセキュリティ警告表示
- コンテンツセキュリティポリシー（CSP）の適用

### 関連するセキュリティベストプラクティス

- OWASP Top 10: Cross-Site Scripting (XSS) 対策
- 入力検証とエスケープ処理のベストプラクティス
- セキュアなHTMLテンプレート設計

## 注意点・制約

- 現時点では基本的なマークダウン構文のみサポート
- テーブル、脚注、定義リストなどの高度な構文は未対応
- ファイルサイズが大きいドキュメントではパフォーマンスに影響
- ブラウザのJavaScript有効化が必須

## 関連知識・参考資料

### 公式ドキュメント

- [Python Regular Expressions](https://docs.python.org/3/library/re.html) - 正規表現の公式ドキュメント
- [MDN Web Docs - HTML](https://developer.mozilla.org/ja/docs/Web/HTML) - HTML仕様とベストプラクティス
- [MDN Web Docs - CSS](https://developer.mozilla.org/ja/docs/Web/CSS) - CSS仕様とレイアウト技法

### 技術解説記事

- [CommonMark Specification](https://spec.commonmark.org/) - マークダウンの標準仕様
- [CSS Grid Layout Guide](https://css-tricks.com/snippets/css/complete-guide-grid/) - CSSグリッドレイアウトの完全ガイド
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - アクセシビリティのガイドライン

### 参考実装・サンプルコード

- [GitHub Markdown CSS](https://github.com/sindresorhus/github-markdown-css) - GitHubスタイルのマークダウンCSS
- [Prism.js](https://prismjs.com/) - シンタックスハイライトライブラリ（将来的な統合候補）

### 関連する概念・知識

- **パーサー設計**: 字句解析と構文解析の基礎
- **DOM操作**: JavaScriptによる動的なDOM更新
- **レスポンシブデザイン**: メディアクエリとフレキシブルレイアウト
- **アクセシビリティ**: セマンティックHTMLとARIA属性の活用
