---
name: doc-to-html
description: Convert markdown documents to readable HTML with floating TOC, copy functionality, and toggle sections. Post-processing skill for /create-doc, /update-doc, /create-investigate-doc, /update-investigate-doc. Requires python3 and scripts/markdown-to-html.py.
allowed-tools:
  - Read
  - Write
  - Bash(python3:*)
user-invocable: true
---

# doc-to-html Skill

Convert markdown documents to readable HTML with table of contents, copy functionality, and toggle sections.

## Features

### 1. Floating Table of Contents
- Fixed position on left side
- Follows scroll
- Click to jump to section
- Highlight current position

### 2. File Path Display
- Display file path on code blocks
- Click to copy path to clipboard
- Visual feedback on copy success

### 3. Toggle by Importance
- Collapsible detail information
- Summary and implementation always visible
- Technical background and references expandable

### 4. Design
- Calm colors (dark gray base)
- Readable font size and line height
- Appropriate contrast ratio
- Responsive support

## Usage

```bash
# Convert specific markdown file to HTML
/doc-to-html path/to/document.md

# Convert all documents in directory to HTML
/doc-to-html path/to/directory/
```

## Generated HTML Structure

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Document Name]</title>
    <style>
        /* Stylesheet */
    </style>
</head>
<body>
    <nav class="toc">
        <!-- Table of Contents -->
    </nav>
    <main class="content">
        <!-- Main Content -->
    </main>
    <script>
        /* Interaction Scripts */
    </script>
</body>
</html>
```

## Markdown to HTML Conversion Rules

### Always Visible Sections
- Summary
- Changed Files
- Implementation

### Toggle Sections (Collapsed by Default)
- Technical Background
- Technical Decisions
- Security Aspects
- Notes/Constraints
- Related Resources

## Output Destination

Generated HTML is saved as `[filename].html` in the same directory as the original markdown file.

Example:
- `task-implementation.md` → `task-implementation.html`

## CSS Variables

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

## JavaScript Features

- TOC active state tracking on scroll
- Smooth scroll navigation
- File path copy to clipboard
- Toggle section expand/collapse
- Mobile menu support

## Customization

To customize HTML design or styles, edit:
- `scripts/markdown-to-html.py` - HTML template and CSS definitions
- `skills/doc-to-html/SKILL.md` - Skill documentation
