# oauth2-authentication

OAuth2とOpenID Connect（OIDC）のフロー選択、トークン管理、実装、セキュリティレビューを支援するAgent Pluginです。

## 読み込み方

Agent Plugins 1.0対応クライアントへ、このディレクトリをプラグインルートとして登録します。

```text
<clone先>/plugins/oauth2-authentication
```

`plugin.json` と `skills/` はクライアントによって自動検出されます。具体的な登録方法やスキルの直接呼び出し構文は、利用するクライアントの手順に従ってください。

## 使い方

読み込み後、OAuth2/OIDCに関する設計、実装、レビュー、調査を自然言語で依頼します。

### フローを選ぶ

```text
React SPAとNode.js APIでユーザー認証を実装します。
利用すべきOAuth2/OIDCフローと、ブラウザ・API間のトークン管理方法を提案してください。
```

### 実装方針を作る

```text
GitHubログインを追加したいです。
Node.jsのサーバーサイドWebアプリを前提に、state検証、callback処理、
セッション管理を含む実装手順を作ってください。
```

### コードをレビューする

```text
このOAuth callbackの実装をレビューしてください。
redirect URI、state、PKCE、トークン保存、エラー処理の問題を確認してください。
```

### 問題を調べる

```text
認可後のcallbackで invalid_grant になります。
認可リクエスト、callback、トークン交換の順に切り分けてください。
```

## 依頼時に伝える情報

次の情報があると、一般論ではなく対象システムに合わせて回答できます。

- アプリケーション種別: サーバーサイドWeb、SPA、モバイル、CLI、M2Mなど
- 認可サーバーまたはIdP: Google、GitHub、Auth0、自社実装など
- クライアントとバックエンドの使用技術
- 認証だけが必要か、外部APIへの認可も必要か
- 現在の構成、関連コード、実際のエラーメッセージ
- redirect URI、scope、token lifetimeなどの制約

client secret、refresh token、authorization codeなどの秘密情報は貼り付けないでください。

## フローの目安

| ユースケース | 主なフロー | 参照資料 |
| --- | --- | --- |
| サーバーサイドWebアプリ | Authorization Code Flow | [`authorization-code.md`](skills/oauth2-authentication/references/authorization-code.md) |
| SPA・モバイルアプリ | Authorization Code Flow with PKCE | [`pkce.md`](skills/oauth2-authentication/references/pkce.md) |
| バックエンド間通信 | Client Credentials Flow | [`client-credentials.md`](skills/oauth2-authentication/references/client-credentials.md) |
| スマートTV・CLI・IoT | Device Authorization Flow | [`device-flow.md`](skills/oauth2-authentication/references/device-flow.md) |

実装対象別の資料も含まれています。

| 対象 | 参照資料 |
| --- | --- |
| React SPA | [`spa-react.md`](skills/oauth2-authentication/references/spa-react.md) |
| Node.jsサーバー | [`server-nodejs.md`](skills/oauth2-authentication/references/server-nodejs.md) |
| モバイルアプリ | [`mobile.md`](skills/oauth2-authentication/references/mobile.md) |
| セキュリティ全般 | [`best-practices.md`](skills/oauth2-authentication/references/best-practices.md) |
| 共通パターン | [`common-patterns.md`](skills/oauth2-authentication/references/common-patterns.md) |

## 利用上の注意

- OAuth2は認可のための仕様です。ユーザー認証が必要な場合はOIDCも含めて設計します。
- provider固有のendpoint、scope、claim、token lifetimeは、対象providerの最新公式資料で確認します。
- Implicit FlowやResource Owner Password Credentials Flowを新規実装へ採用しません。
- 公開クライアントではPKCEを使用し、redirect URI、state、issuer、audience、署名、有効期限を用途に応じて検証します。
- スキルの出力は実装支援であり、対象providerの設定やセキュリティ要件への適合を自動的に保証するものではありません。
