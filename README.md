# yibuki-cc-plugins

[Agent Plugins 1.0](https://agent-plugins.org/specification) に準拠した、個人用のAgent Pluginコレクションです。各 `plugins/<name>/` ディレクトリが独立したプラグインパッケージです。

## プラグイン

| 名前 | 概要 |
| --- | --- |
| `dispatch-team` | 独立した作業を複数エージェントへ分割して並列実行する |
| `lang-learner` | 公式ドキュメントを根拠にプログラミング言語を学ぶ |
| `oauth2-authentication` | OAuth2とOpenID Connectの実装・セキュリティガイド |
| `save-article-summary` | 記事を要約してYoyaku形式のJSONへ保存する |

## パッケージ構成

```text
plugins/<plugin-name>/
├── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── references/   # 任意
        ├── scripts/      # 任意
        └── assets/       # 任意
```

- `plugin.json` はルート直下に置き、Agent Plugins 1.0の `$schema` を宣言します。
- スキルは `skills/` の直下に1ディレクトリずつ置き、Agent Skills仕様へ準拠させます。
- MCPサーバーを追加する場合は、ルート直下の `mcp.json` を使用します。
- Agent Plugins v1の標準コンポーネントはSkillsとMCPのみです。コマンド、フック、カスタムエージェントなどのクライアント固有機能は、必要な場合だけreverse-domain namespaceのextensionとして分離します。

## 新しいプラグインの追加

1. `plugins/<plugin-name>/plugin.json` を作成します。
2. `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` を作成します。
3. manifestと各スキルをschemaおよびAgent Skillsの規則で検証します。

```bash
ruby scripts/validate-agent-plugins.rb
```

最小manifest:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "plugin-name"
}
```

Agent Pluginsはパッケージ形式を標準化しますが、インストール方法はクライアントごとに異なります。利用するクライアントのAgent Plugins対応状況と導入手順を確認してください。
