---
name: search-related-docs
description: Search and identify related documents to complement context during command execution. Triggers on /create-doc, /update-doc, /create-investigate-doc, /update-investigate-doc. Uses git status to detect changed files and matches against existing documents in .claude/custom-documents/.
allowed-tools:
  - Read
  - Glob
  - Bash(git status:*)
  - Bash(git diff:*)
---

# search-related-docs Skill

Internal skill for searching and identifying related documents during command execution.

## Purpose

When executing `/create-doc` or `/update-doc`:
1. Automatically search for related documents
2. Present highly relevant documents as candidates
3. Request user confirmation when needed

## Search Logic

### Search Target
```
.claude/custom-documents/
├── feature-auth-login/
├── api-refactor/
└── ...
```

### Relevance Scoring Criteria

| Factor | Weight | Description |
|--------|--------|-------------|
| File match | High | Documents that modified the same files |
| Directory match | High | Documents handling files in the same directory |
| Keyword match | Medium | Same keywords in summary or implementation |
| Tech stack match | Medium | Same technologies or libraries used |
| Temporal proximity | Low | Recently updated documents |

### Search Flow

```
1. Get current changed files from git status/diff
2. Compare with "Changed Files" section in each document
3. Calculate relevance score
4. Sort by score
5. Return documents above threshold as candidates
```

## Usage (Internal Command Call)

### Basic Search

```markdown
## Related Document Search

Search for related documents with the following steps:

1. Scan all directories in `.claude/custom-documents/`
2. Parse each document's content
3. Calculate relevance to current changed files
4. List highly relevant documents
```

### Result Presentation Format

```markdown
📚 Potentially related documents found:

1. **feature-auth-login** (Relevance: High)
   - Matches: `src/auth/login.ts`, `src/auth/middleware.ts`
   - Summary: Login feature implementation

2. **api-auth-system** (Relevance: Medium)
   - Matches: `src/auth/` directory
   - Summary: Authentication API design

Would you like to reference these documents?
- (y) Yes, load as context
- (n) No, create as new document
- (1-2) Select specific document only
```

## Command Integration Examples

### Usage in create-doc

```markdown
## Pre-creation Check

Before document creation, reference `skills/search-related-docs`:

1. Search for related documents
2. If highly relevant documents found, ask for confirmation
3. Based on user selection:
   - Update existing document → redirect to /update-doc
   - Continue with new creation
   - Create new with existing document as context reference
```

### Usage in update-doc

```markdown
## Target Identification

Use `skills/search-related-docs` to:

1. Identify most relevant document to current changes
2. If multiple candidates, ask for selection
3. Show warning if relevance is low
```

## Output Format

### Search Result Object (Internal)

```yaml
results:
  - name: "feature-auth-login"
    path: ".claude/custom-documents/feature-auth-login/"
    relevance: high
    matched_files:
      - "src/auth/login.ts"
      - "src/auth/middleware.ts"
    summary: "Login feature implementation"
    last_updated: "2024-11-20"

  - name: "api-auth-system"
    path: ".claude/custom-documents/api-auth-system/"
    relevance: medium
    matched_files: []
    matched_directory: "src/auth/"
    summary: "Authentication API design"
    last_updated: "2024-11-15"
```

## Notes

- Search targets Markdown files only
- Case-insensitive matching
- Partial match search (exact match not required)
- Limit to top 5 results if too many matches
