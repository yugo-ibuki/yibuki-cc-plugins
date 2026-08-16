# AGENTS.md

## Project overview

このリポジトリは、[Agent Plugins 1.0](https://agent-plugins.org/specification) に準拠するAgent Pluginコレクションです。各 `plugins/<name>/` は独立して配布・読み込みできるskills-only pluginです。

## Architecture

```text
plugins/<plugin-name>/
├── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── references/
```

## Manifest rules

- manifestは必ず `plugins/<plugin-name>/plugin.json` に置く。
- `$schema` は `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` を使用する。
- `name` はディレクトリ名と一致させ、Agent Pluginsの命名制約を守る。
- 未定義のtop-level fieldを追加しない。クライアント固有情報は `extensions` のreverse-domain namespaceへ置く。
- コンポーネントパスをmanifestへ記載しない。Skillsは `skills/`、MCPは `mcp.json` の固定位置から検出される。

## Skill rules

- スキルは `skills/<skill-name>/SKILL.md` に置く。再帰的なスキル検出に依存しない。
- frontmatterの `name` は親ディレクトリ名と一致させる。
- `description` には機能と使用条件を具体的に記載する。
- 詳細資料は同じスキルの `references/` に置き、`SKILL.md` から相対パスで参照する。
- クライアント固有のtool名やslash commandを必須前提にしない。

## Scope

Agent Plugins v1のportable componentはSkillsとMCPのみです。`commands/`、hooks、custom agents、rules、LSPは標準コンポーネントとして追加しません。必要になった場合は、portable coreと分離したclient extensionとして実装します。

## Verification

変更後は以下を確認します。

1. すべてのplugin rootに有効な `plugin.json` がある。
2. すべてのskillがAgent Skills仕様のfrontmatterと命名規則を満たす。
3. `SKILL.md` から参照する相対ファイルが存在する。
4. Claude固有の `.claude-plugin` や `commands/` が残っていない。
5. `git diff --check` が成功する。

リポジトリ全体の構造、manifest、skill frontmatter、相対リンクは次のコマンドで検証する。

```bash
ruby scripts/validate-agent-plugins.rb
```

ユーザー向けテキストは日本語を基本とし、ユーザーの未コミット変更を保持する。
