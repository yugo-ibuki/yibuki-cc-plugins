# agent-plugins

[Agent Plugins 1.0](https://agent-plugins.org/specification) に準拠した、個人用のAgent Pluginコレクションです。各 `plugins/<name>/` ディレクトリを独立したプラグインパッケージとして利用できます。

## 利用できるプラグイン

| プラグイン | 含まれるスキル | 用途 |
| --- | --- | --- |
| [`dispatch-team`](plugins/dispatch-team/) | `dispatch-team` | 独立した作業を複数エージェントへ分割して並列実行する |
| [`lang-learner`](plugins/lang-learner/) | `lang-learner`、`doc-lookup`、`concept-explainer` | 公式ドキュメントを根拠にプログラミング言語を学ぶ |
| [`oauth2-authentication`](plugins/oauth2-authentication/) | `oauth2-authentication` | OAuth2とOpenID Connectの設計・実装・セキュリティを支援する |
| [`save-article-summary`](plugins/save-article-summary/) | `save-article-summary` | 記事を要約してYoyaku形式のJSONへ保存する |

## 使い方

### 1. リポジトリを取得する

```bash
git clone https://github.com/yugo-ibuki/agent-plugins.git
cd agent-plugins
```

### 2. 利用するプラグインを読み込む

Agent Plugins 1.0対応クライアントへ、利用したいプラグインのルートディレクトリを登録します。

```text
<clone先>/plugins/<plugin-name>
```

たとえば `lang-learner` を使う場合、登録するディレクトリは `plugins/lang-learner/` です。リポジトリ全体や個別の `SKILL.md` ではなく、`plugin.json` があるプラグインルートを指定してください。

インストール、ローカルディレクトリの登録、更新方法はクライアントごとに異なります。利用するクライアントのAgent Plugins対応状況と導入手順を確認してください。このリポジトリには、特定クライアント専用のslash commandやhookは含まれていません。

### 3. 自然言語で依頼する

読み込み後は、各スキルの使用条件に合う内容を自然言語で依頼します。スキル名を明示することもできますが、呼び出し構文はクライアントに依存します。

## プラグイン別の利用例

### dispatch-team

互いに独立しており、同じファイルや状態を共有しない複数の作業を並列化したいときに使います。エージェント委譲機能を持つクライアントが必要です。

```text
失敗している3つのテストファイルは原因が独立していそうです。
ファイルごとに担当を分けて並列に調査し、修正内容を統合してください。
```

関連する障害、同じファイルを編集する作業、前の結果が次の入力になる作業には向きません。

### lang-learner

新しいプログラミング言語や言語機能を、公式ドキュメント、コード例、他言語との比較を使って学びたいときに使います。

```text
Rustのownershipとborrowingを、TypeScriptと比較しながら説明してください。
公式ドキュメントへのリンクと、よくある間違いも含めてください。
```

公式情報の取得には、クライアントが提供するドキュメント検索またはWebアクセスを使用します。利用できない場合は、取得できなかった根拠を明示したうえで回答範囲を限定します。

### oauth2-authentication

アプリケーションに適したOAuth2/OIDCフローの選択、実装方針、コードレビュー、認証エラーの調査に使います。

```text
React SPAとNode.js APIにGoogleログインを追加したいです。
Authorization Code Flow with PKCEを前提に、トークンの保存場所と検証方法を設計してください。
```

より正確な案を得るには、アプリ種別、認可サーバー、使用技術、現在の構成、解決したい問題を伝えてください。詳細は [`plugins/oauth2-authentication/README.md`](plugins/oauth2-authentication/README.md) を参照してください。

### save-article-summary

記事URLを渡し、本文を根拠に日本語で要約してYoyakuの `summary-articles` リポジトリへ保存したいときに使います。

```text
この記事を要約してYoyakuに保存してください。
https://example.com/article
```

対象リポジトリには `article.schema.json`、`content/articles/`、`package.json` の `validate:data` が必要です。該当する現在のリポジトリがない場合は、スキル既定の `summary-articles` リポジトリを探します。通常の「保存」はローカルファイルの更新までで、コミット、push、デプロイは明示的に依頼された場合だけ行います。

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
- Agent Plugins v1の標準コンポーネントはSkillsとMCPのみです。クライアント固有機能は、必要な場合だけportable coreと分離します。

## 開発と検証

新しいプラグインを追加する場合は、次の最小構成を作成します。

1. `plugins/<plugin-name>/plugin.json`
2. `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
3. 必要に応じて、同じスキル内の `references/`、`scripts/`、`assets/`

最小manifest:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "plugin-name"
}
```

構造、manifest、skill frontmatter、相対リンクをまとめて検証します。

```bash
ruby scripts/validate-agent-plugins.rb
git diff --check
```
