---
name: doc-to-html
description: Convert markdown documents to readable HTML with floating TOC, copy functionality, and toggle sections
version: 1.0.0
author: yugo-ibuki
keywords:
  - html
  - markdown
  - conversion
  - toc
  - documentation
  - responsive
used-by:
  - /create-doc (post-processing)
  - /update-doc (post-processing)
  - /create-investigate-doc (post-processing)
  - /update-investigate-doc (post-processing)
dependencies:
  - python3
  - scripts/markdown-to-html.py
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

## HTMLテンプレート

生成されるHTMLには以下の要素が含まれます：

### CSS（スタイルシート）
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

body {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}

/* 目次スタイル */
.toc {
    position: fixed;
    left: 0;
    top: 0;
    width: 280px;
    height: 100vh;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 2rem 1rem;
    box-sizing: border-box;
}

.toc-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--accent);
}

.toc-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.toc-item {
    margin-bottom: 0.5rem;
}

.toc-link {
    display: block;
    padding: 0.5rem 0.75rem;
    color: var(--text-secondary);
    text-decoration: none;
    border-radius: 4px;
    transition: all 0.2s ease;
    font-size: 0.95rem;
}

.toc-link:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.toc-link.active {
    background: var(--accent);
    color: white;
}

.toc-item.level-2 {
    padding-left: 1rem;
}

.toc-item.level-3 {
    padding-left: 2rem;
}

/* メインコンテンツ */
.content {
    margin-left: 300px;
    padding: 2rem 3rem;
    max-width: 1200px;
}

/* 見出し */
h1 {
    font-size: 2.5rem;
    margin: 0 0 2rem 0;
    color: var(--text-primary);
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.5rem;
}

h2 {
    font-size: 1.8rem;
    margin: 3rem 0 1rem 0;
    color: var(--text-primary);
    position: relative;
    padding-left: 1rem;
}

h2::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 70%;
    background: var(--accent);
    border-radius: 2px;
}

h3 {
    font-size: 1.4rem;
    margin: 2rem 0 0.75rem 0;
    color: var(--text-primary);
}

/* コードブロック */
.code-block {
    position: relative;
    margin: 1.5rem 0;
}

.file-path {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 0.75rem 1rem;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9rem;
    color: var(--accent);
}

.copy-button {
    background: var(--accent);
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}

.copy-button:hover {
    background: var(--accent-hover);
}

.copy-button.copied {
    background: var(--success);
}

pre {
    margin: 0;
    padding: 1.5rem;
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 0 0 6px 6px;
    overflow-x: auto;
}

code {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* インラインコード */
:not(pre) > code {
    background: var(--bg-tertiary);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.9em;
}

/* トグル（詳細セクション） */
.toggle-section {
    margin: 1.5rem 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
}

.toggle-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: var(--bg-secondary);
    cursor: pointer;
    transition: background 0.2s ease;
    user-select: none;
}

.toggle-header:hover {
    background: var(--bg-tertiary);
}

.toggle-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.toggle-icon {
    font-size: 1.2rem;
    color: var(--text-secondary);
    transition: transform 0.3s ease;
}

.toggle-section.expanded .toggle-icon {
    transform: rotate(180deg);
}

.toggle-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.toggle-section.expanded .toggle-content {
    max-height: 5000px;
}

.toggle-inner {
    padding: 1.5rem;
}

/* リスト */
ul, ol {
    margin: 1rem 0;
    padding-left: 2rem;
}

li {
    margin: 0.5rem 0;
}

/* リンク */
a {
    color: var(--accent);
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: var(--accent-hover);
    text-decoration: underline;
}

/* レスポンシブ対応 */
@media (max-width: 1024px) {
    .toc {
        width: 250px;
    }

    .content {
        margin-left: 270px;
        padding: 1.5rem 2rem;
    }
}

@media (max-width: 768px) {
    .toc {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        z-index: 1000;
    }

    .toc.mobile-open {
        transform: translateX(0);
    }

    .content {
        margin-left: 0;
        padding: 1rem;
    }

    .mobile-menu-button {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999;
        background: var(--accent);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 4px;
        cursor: pointer;
    }
}
```

### JavaScript（インタラクション）
```javascript
document.addEventListener('DOMContentLoaded', function() {
    // 目次のアクティブ状態更新
    const sections = document.querySelectorAll('h2, h3');
    const tocLinks = document.querySelectorAll('.toc-link');

    function updateActiveLink() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });

        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();

    // スムーススクロール
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ファイルパスコピー機能
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', function() {
            const filePath = this.getAttribute('data-path');
            navigator.clipboard.writeText(filePath).then(() => {
                const originalText = this.textContent;
                this.textContent = 'コピー完了!';
                this.classList.add('copied');

                setTimeout(() => {
                    this.textContent = originalText;
                    this.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('コピー失敗:', err);
            });
        });
    });

    // トグル機能
    document.querySelectorAll('.toggle-header').forEach(header => {
        header.addEventListener('click', function() {
            const section = this.parentElement;
            section.classList.toggle('expanded');
        });
    });

    // モバイルメニュー
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const toc = document.querySelector('.toc');

    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            toc.classList.toggle('mobile-open');
        });
    }
});
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
