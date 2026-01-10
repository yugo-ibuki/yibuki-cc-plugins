---
name: load-doc-context
description: Load documents and incorporate them as session context for seamless workflow continuation. Triggers after search-related-docs finds matches. Parses markdown structure, extracts file lists, and generates context summaries for worktree-based parallel development.
allowed-tools:
  - Read
  - Glob
---

# load-doc-context Skill

Internal skill for loading documents and incorporating them as session context.

## Purpose

For documents identified by search:
1. Load and parse content
2. Extract important information
3. Utilize as current session context

## Loading Flow

```
1. Receive target document path
2. List .md files in directory
3. Load each file's content
4. Generate structured context
5. Incorporate into session
```

## Extracted Information

### Required Items

| Section | Extracted Content | Usage |
|---------|-------------------|-------|
| Summary | Overall description | Context understanding |
| Changed Files | File path list | Duplicate check, relevance judgment |
| Implementation | Specific changes | Implementation reference |

### Optional Items (Extract if Present)

| Section | Extracted Content | Usage |
|---------|-------------------|-------|
| Technical Background | Technical information | Implementation decision reference |
| Technical Decisions | Design rationale | Maintain consistency |
| Notes/Constraints | Constraints | Avoid issues |
| Security Aspects | Security measures | Ensure security |

## Output Format

### Context Summary

```markdown
---
📚 Context loaded: feature-auth-login
---

## Summary
Login feature implementation. Session management using JWT authentication.

## Previously Changed Files
- `src/auth/login.ts` - Login processing
- `src/auth/middleware.ts` - Auth middleware
- `src/auth/types.ts` - Type definitions

## Key Implementation Points
- JWT token generation and validation
- Refresh token implementation
- Session expiration management

## Notes
- Token expiration set via environment variable
- Refresh token stored in HTTPOnly Cookie

---
💡 Continuing work with this context
```

## Command Integration

### Integration with search-related-docs

```markdown
## Flow When Related Documents Found

1. `search-related-docs` searches for related documents
2. If user selects reference:
   - `load-doc-context` loads context
   - Display summary
3. Continue work with context
```

### Usage in create-doc

```markdown
## Reference During New Creation

When related document loaded as context:

1. Check consistency with past implementation
2. Consider append format if changes to same file
3. Maintain consistency in technical decisions
4. Inherit notes and constraints
```

### Usage in update-doc

```markdown
## Diff Detection During Update

Load existing document:

1. Extract documented files from "Changed Files" section
2. Compare with current changed files
3. Identify only undocumented files as append targets
```

## Loading Options

| Option | Description | Default |
|--------|-------------|---------|
| full | Load all sections | false |
| summary_only | Summary only | false |
| files_only | Changed files only | false |
| exclude_security | Exclude security items | false |

## Error Handling

### Document Not Found

```markdown
⚠️ Specified document not found: feature-xxx

Please verify:
- Directory name is correct
- Exists under `.claude/custom-documents/`
```

### Loading Error

```markdown
⚠️ Failed to load document: feature-auth-login

Cause: File may be empty or corrupted
Action: Please check the directory contents
```

## Notes

- HTML files are not loaded (Markdown only)
- Large documents (>1000 lines) are summarized before loading
- Multiple files are merged and processed
- Loaded context is valid only within session
