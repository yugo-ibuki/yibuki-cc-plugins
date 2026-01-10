# Custom Document Skills

Skill definitions for the custom document plugin.

## Directory Structure

```
skills/
├── README.md
├── search-related-docs/
│   └── SKILL.md
├── load-doc-context/
│   └── SKILL.md
└── doc-to-html/
│   └── SKILL.md
├── example-doc.md
└── example-doc.html
```

## Skills Overview

### search-related-docs (Internal Skill)

Skill for searching and identifying related documents during command execution.

**Triggers:** `/create-doc`, `/update-doc`, `/create-investigate-doc`, `/update-investigate-doc`

**Features:**
- Compare git status changed files against existing documents
- Relevance scoring (file match, directory match, keyword match)
- Present highly relevant documents as candidates
- Request user confirmation

### load-doc-context (Internal Skill)

Skill for loading documents and incorporating them as session context.

**Triggers:** `/create-doc`, `/update-doc`, `/create-investigate-doc`, `/update-investigate-doc`

**Features:**
- Parse and structure document content
- Extract documented file list
- Generate context summary
- Diff detection (for update-doc, update-investigate-doc)

---

### doc-to-html (User-Invocable Skill)

Skill for converting markdown documents to readable HTML.

**Features:**
- Floating table of contents (scroll tracking)
- One-click file path copy
- Toggle expand for detail sections
- Dark mode design with calm colors
- Responsive support

**Usage:**

```bash
# Convert single file
python plugins/custom-doc/scripts/markdown-to-html.py path/to/document.md

# Convert all markdown in directory
python plugins/custom-doc/scripts/markdown-to-html.py path/to/directory/
```

**Generated HTML:**

- Floating TOC on left side
- Main content area with sufficient width
- Code blocks with file path display and copy button
- Collapsible technical details
- Dark gray base calm design

## Sample

`example-doc.md` and `example-doc.html` are provided as samples.

Open the HTML in a browser to check the features:

```bash
open plugins/custom-doc/skills/example-doc.html
```

## Adding New Skills

To add a new skill, create a directory with `SKILL.md` file:

```
skills/
└── new-skill-name/
    └── SKILL.md
```

SKILL.md format:

```markdown
---
name: skill-name
description: Skill description (used for auto-invocation matching)
allowed-tools:
  - Read
  - Write
  - Bash(specific:*)
user-invocable: false  # true if can be invoked by user
---

# Skill Name

Detailed skill description...
```

## Official Frontmatter Fields

| Field | Description |
|-------|-------------|
| name | Skill name |
| description | Description (used for auto-invocation matching) |
| allowed-tools | Tools the skill can use |
| model | Model to use (optional) |
| context | Context files to include (optional) |
| agent | Agent configuration (optional) |
| hooks | Pre/post execution hooks (optional) |
| user-invocable | Whether user can invoke directly (default: false) |
| disable-model-invocation | Prevent model from auto-invoking (optional) |
