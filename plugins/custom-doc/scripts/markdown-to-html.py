#!/usr/bin/env python3
"""
マークダウンドキュメントをHTML化するスクリプト
目次、コピー機能、トグル展開機能を備えたHTMLを生成
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


def extract_headings(markdown_content: str) -> List[Tuple[int, str, str]]:
    """
    マークダウンから見出しを抽出
    Returns: [(level, id, text), ...]
    """
    headings = []
    for line in markdown_content.split('\n'):
        match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            heading_id = re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '-').lower()
            headings.append((level, heading_id, text))
    return headings


def generate_toc(headings: List[Tuple[int, str, str]]) -> str:
    """目次HTMLを生成"""
    toc_html = '<div class="toc-title">目次</div>\n<ul class="toc-list">\n'

    for level, heading_id, text in headings:
        if level <= 3:  # h1-h3まで
            toc_html += f'  <li class="toc-item level-{level}">'
            toc_html += f'<a href="#{heading_id}" class="toc-link">{text}</a></li>\n'

    toc_html += '</ul>'
    return toc_html


def detect_toggle_sections() -> Dict[str, str]:
    """トグル展開対象のセクション名を定義"""
    return {
        "技術的な背景・解説": "技術的な背景と詳細な解説",
        "技術的な判断・設計決定": "設計判断の詳細",
        "セキュリティ観点": "セキュリティの詳細情報",
        "注意点・制約": "注意事項と制約",
        "関連知識・参考資料": "参考資料とリンク"
    }


def parse_code_block(content: str) -> str:
    """コードブロックをファイルパス付きHTMLに変換"""
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)

        # ファイルパスを検出（最初の行がパスっぽい場合）
        lines = code.split('\n')
        file_path = None
        code_content = code

        if lines and ('/' in lines[0] or '\\' in lines[0]) and not lines[0].strip().startswith('#'):
            # 最初の行がパスの可能性
            potential_path = lines[0].strip()
            if re.match(r'^[\w\-./\\]+\.\w+$', potential_path):
                file_path = potential_path
                code_content = '\n'.join(lines[1:])

        html = '<div class="code-block">\n'

        if file_path:
            html += f'  <div class="file-path">\n'
            html += f'    <span>{file_path}</span>\n'
            html += f'    <button class="copy-button" data-path="{file_path}">コピー</button>\n'
            html += f'  </div>\n'

        html += f'  <pre><code class="language-{lang}">{escape_html(code_content)}</code></pre>\n'
        html += '</div>'

        return html

    # コードブロックを置換
    pattern = r'```(\w+)?\n(.*?)```'
    return re.sub(pattern, replace_code_block, content, flags=re.DOTALL)


def escape_html(text: str) -> str:
    """HTML特殊文字をエスケープ"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def convert_inline_code(text: str) -> str:
    """インラインコードを変換"""
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', text)


def convert_links(text: str) -> str:
    """マークダウンリンクをHTMLに変換"""
    # [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def convert_bold_italic(text: str) -> str:
    """太字・斜体を変換"""
    # **bold**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # *italic*
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def process_markdown_content(content: str) -> str:
    """マークダウンコンテンツをHTMLに変換"""
    toggle_sections = detect_toggle_sections()

    # コードブロックを先に処理（他の変換から保護）
    content = parse_code_block(content)

    lines = content.split('\n')
    html_lines = []
    in_list = False
    in_toggle = False
    toggle_content = []
    current_toggle_title = ""

    i = 0
    while i < len(lines):
        line = lines[i]

        # 見出し処理
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if heading_match:
            # リスト終了
            if in_list:
                html_lines.append('</ul>')
                in_list = False

            # 前のトグルを閉じる
            if in_toggle:
                toggle_html = generate_toggle_section(current_toggle_title, '\n'.join(toggle_content))
                html_lines.append(toggle_html)
                in_toggle = False
                toggle_content = []

            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            heading_id = re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '-').lower()

            # トグルセクションかチェック
            if text in toggle_sections:
                in_toggle = True
                current_toggle_title = toggle_sections[text]
                i += 1
                continue

            html_lines.append(f'<h{level} id="{heading_id}">{text}</h{level}>')
            i += 1
            continue

        # トグルセクション内の処理
        if in_toggle:
            # 次の見出しまでコンテンツを収集
            if not line.startswith('#'):
                toggle_content.append(line)
            i += 1
            continue

        # リスト処理
        list_match = re.match(r'^[-*]\s+(.+)$', line)
        if list_match:
            if not in_list:
                html_lines.append('<ul>')
                in_list = True

            item_text = list_match.group(1)
            item_text = convert_inline_code(item_text)
            item_text = convert_links(item_text)
            item_text = convert_bold_italic(item_text)
            html_lines.append(f'  <li>{item_text}</li>')
            i += 1
            continue

        # リスト終了
        if in_list and line.strip() == '':
            html_lines.append('</ul>')
            in_list = False
            i += 1
            continue

        # 通常の段落
        if line.strip() and not line.startswith('<'):
            line = convert_inline_code(line)
            line = convert_links(line)
            line = convert_bold_italic(line)
            html_lines.append(f'<p>{line}</p>')
        elif line.startswith('<'):
            # すでにHTML（コードブロック等）
            html_lines.append(line)

        i += 1

    # 最後のリストやトグルを閉じる
    if in_list:
        html_lines.append('</ul>')
    if in_toggle:
        toggle_html = generate_toggle_section(current_toggle_title, '\n'.join(toggle_content))
        html_lines.append(toggle_html)

    return '\n'.join(html_lines)


def generate_toggle_section(title: str, content: str) -> str:
    """トグルセクションのHTMLを生成"""
    html = '<div class="toggle-section">\n'
    html += '  <div class="toggle-header">\n'
    html += f'    <div class="toggle-title">{title}</div>\n'
    html += '    <div class="toggle-icon">▼</div>\n'
    html += '  </div>\n'
    html += '  <div class="toggle-content">\n'
    html += '    <div class="toggle-inner">\n'

    # コンテンツ内のマークダウンを処理
    content_lines = content.strip().split('\n')
    processed_lines = []

    for line in content_lines:
        if line.strip():
            # リスト
            if re.match(r'^[-*]\s+', line):
                if not processed_lines or not processed_lines[-1].startswith('<ul>'):
                    processed_lines.append('<ul>')
                item_text = re.sub(r'^[-*]\s+', '', line)
                item_text = convert_inline_code(item_text)
                item_text = convert_links(item_text)
                processed_lines.append(f'  <li>{item_text}</li>')
            else:
                # リスト終了
                if processed_lines and processed_lines[-1].startswith('  <li>'):
                    processed_lines.append('</ul>')

                line = convert_inline_code(line)
                line = convert_links(line)
                processed_lines.append(f'<p>{line}</p>')

    # 最後のリストを閉じる
    if processed_lines and processed_lines[-1].startswith('  <li>'):
        processed_lines.append('</ul>')

    html += '\n'.join(processed_lines)
    html += '\n    </div>\n'
    html += '  </div>\n'
    html += '</div>'

    return html


def get_html_template() -> str:
    """HTMLテンプレートを取得"""
    return '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
:root {{
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
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}}

.toc {{
    position: fixed;
    left: 0;
    top: 0;
    width: 280px;
    height: 100vh;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 2rem 1rem;
}}

.toc-title {{
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--accent);
}}

.toc-list {{
    list-style: none;
    padding: 0;
    margin: 0;
}}

.toc-item {{
    margin-bottom: 0.5rem;
}}

.toc-link {{
    display: block;
    padding: 0.5rem 0.75rem;
    color: var(--text-secondary);
    text-decoration: none;
    border-radius: 4px;
    transition: all 0.2s ease;
    font-size: 0.95rem;
}}

.toc-link:hover {{
    background: var(--bg-tertiary);
    color: var(--text-primary);
}}

.toc-link.active {{
    background: var(--accent);
    color: white;
}}

.toc-item.level-2 {{
    padding-left: 1rem;
}}

.toc-item.level-3 {{
    padding-left: 2rem;
}}

.content {{
    margin-left: 300px;
    padding: 2rem 3rem;
    max-width: 1200px;
}}

h1 {{
    font-size: 2.5rem;
    margin: 0 0 2rem 0;
    color: var(--text-primary);
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.5rem;
}}

h2 {{
    font-size: 1.8rem;
    margin: 3rem 0 1rem 0;
    color: var(--text-primary);
    position: relative;
    padding-left: 1rem;
}}

h2::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 70%;
    background: var(--accent);
    border-radius: 2px;
}}

h3 {{
    font-size: 1.4rem;
    margin: 2rem 0 0.75rem 0;
    color: var(--text-primary);
}}

p {{
    margin: 1rem 0;
}}

.code-block {{
    position: relative;
    margin: 1.5rem 0;
}}

.file-path {{
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
}}

.copy-button {{
    background: var(--accent);
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}}

.copy-button:hover {{
    background: var(--accent-hover);
}}

.copy-button.copied {{
    background: var(--success);
}}

pre {{
    margin: 0;
    padding: 1.5rem;
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 0 0 6px 6px;
    overflow-x: auto;
}}

.file-path + pre {{
    border-radius: 0 0 6px 6px;
}}

code {{
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    color: var(--text-primary);
}}

:not(pre) > code {{
    background: var(--bg-tertiary);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.9em;
}}

.toggle-section {{
    margin: 1.5rem 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
}}

.toggle-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: var(--bg-secondary);
    cursor: pointer;
    transition: background 0.2s ease;
    user-select: none;
}}

.toggle-header:hover {{
    background: var(--bg-tertiary);
}}

.toggle-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}}

.toggle-icon {{
    font-size: 1.2rem;
    color: var(--text-secondary);
    transition: transform 0.3s ease;
}}

.toggle-section.expanded .toggle-icon {{
    transform: rotate(180deg);
}}

.toggle-content {{
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}}

.toggle-section.expanded .toggle-content {{
    max-height: 5000px;
}}

.toggle-inner {{
    padding: 1.5rem;
}}

ul, ol {{
    margin: 1rem 0;
    padding-left: 2rem;
}}

li {{
    margin: 0.5rem 0;
}}

a {{
    color: var(--accent);
    text-decoration: none;
    transition: color 0.2s ease;
}}

a:hover {{
    color: var(--accent-hover);
    text-decoration: underline;
}}

strong {{
    color: var(--text-primary);
    font-weight: 600;
}}

@media (max-width: 1024px) {{
    .toc {{
        width: 250px;
    }}

    .content {{
        margin-left: 270px;
        padding: 1.5rem 2rem;
    }}
}}

@media (max-width: 768px) {{
    .toc {{
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        z-index: 1000;
    }}

    .toc.mobile-open {{
        transform: translateX(0);
    }}

    .content {{
        margin-left: 0;
        padding: 1rem;
    }}

    .mobile-menu-button {{
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
        display: block;
    }}
}}

.mobile-menu-button {{
    display: none;
}}
    </style>
</head>
<body>
    <button class="mobile-menu-button">☰ メニュー</button>

    <nav class="toc">
        {toc}
    </nav>

    <main class="content">
        {content}
    </main>

    <script>
document.addEventListener('DOMContentLoaded', function() {{
    const sections = document.querySelectorAll('h1, h2, h3');
    const tocLinks = document.querySelectorAll('.toc-link');

    function updateActiveLink() {{
        let current = '';
        sections.forEach(section => {{
            const sectionTop = section.offsetTop;
            if (pageYOffset >= sectionTop - 100) {{
                current = section.getAttribute('id');
            }}
        }});

        tocLinks.forEach(link => {{
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {{
                link.classList.add('active');
            }}
        }});
    }}

    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();

    tocLinks.forEach(link => {{
        link.addEventListener('click', function(e) {{
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {{
                targetElement.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
            }}
        }});
    }});

    document.querySelectorAll('.copy-button').forEach(button => {{
        button.addEventListener('click', function() {{
            const filePath = this.getAttribute('data-path');
            navigator.clipboard.writeText(filePath).then(() => {{
                const originalText = this.textContent;
                this.textContent = 'コピー完了!';
                this.classList.add('copied');

                setTimeout(() => {{
                    this.textContent = originalText;
                    this.classList.remove('copied');
                }}, 2000);
            }}).catch(err => {{
                console.error('コピー失敗:', err);
            }});
        }});
    }});

    document.querySelectorAll('.toggle-header').forEach(header => {{
        header.addEventListener('click', function() {{
            const section = this.parentElement;
            section.classList.toggle('expanded');
        }});
    }});

    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const toc = document.querySelector('.toc');

    if (mobileMenuButton) {{
        mobileMenuButton.addEventListener('click', function() {{
            toc.classList.toggle('mobile-open');
        }});
    }}
}});
    </script>
</body>
</html>'''


def convert_markdown_to_html(markdown_file: Path, output_file: Path = None) -> Path:
    """マークダウンファイルをHTMLに変換"""

    # マークダウンを読み込み
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # タイトルを抽出（最初のh1）
    title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else markdown_file.stem

    # 見出しを抽出して目次を生成
    headings = extract_headings(markdown_content)
    toc_html = generate_toc(headings)

    # マークダウンをHTMLに変換
    content_html = process_markdown_content(markdown_content)

    # HTMLテンプレートに埋め込み
    html_template = get_html_template()
    final_html = html_template.format(
        title=title,
        toc=toc_html,
        content=content_html
    )

    # 出力ファイル名を決定
    if output_file is None:
        output_file = markdown_file.with_suffix('.html')

    # HTMLを書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

    return output_file


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python markdown-to-html.py <markdown_file_or_directory>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        sys.exit(1)

    # ディレクトリの場合は全マークダウンファイルを変換
    if input_path.is_dir():
        markdown_files = list(input_path.glob('*.md'))
        if not markdown_files:
            print(f"No markdown files found in {input_path}")
            sys.exit(1)

        print(f"Found {len(markdown_files)} markdown file(s)")
        for md_file in markdown_files:
            print(f"Converting {md_file.name}...", end=' ')
            output_file = convert_markdown_to_html(md_file)
            print(f"✓ {output_file.name}")

    # ファイルの場合は単一変換
    elif input_path.is_file():
        if input_path.suffix != '.md':
            print(f"Error: {input_path} is not a markdown file")
            sys.exit(1)

        print(f"Converting {input_path.name}...", end=' ')
        output_file = convert_markdown_to_html(input_path)
        print(f"✓ {output_file.name}")

    print("\n✨ Conversion complete!")


if __name__ == '__main__':
    main()
