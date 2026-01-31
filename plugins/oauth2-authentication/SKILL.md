---
name: oauth2-authentication
description: Comprehensive OAuth2 authentication skill covering authorization flows, token management, PKCE, OpenID Connect, and security best practices for modern authentication systems
---

# OAuth2 Authentication Skill

OAuth2認証とOpenID Connectの包括的な実装ガイド。

## When to Use This Skill

- Webアプリ、SPA、モバイルアプリでのユーザー認証実装
- アクセストークンとリフレッシュトークンによるAPI認可
- ソーシャルログイン統合（Google, GitHub, Facebook等）
- マシン間（M2M）認証の構築
- シングルサインオン（SSO）の実装
- OAuth2認可サーバーの構築

## File Navigation Guide

### フローの選択

| ユースケース | 参照ファイル |
|-------------|-------------|
| サーバーサイドWebアプリ | [flows/authorization-code.md](./flows/authorization-code.md) |
| SPA・モバイルアプリ | [flows/pkce.md](./flows/pkce.md) |
| バックエンドサービス間通信 | [flows/client-credentials.md](./flows/client-credentials.md) |
| スマートTV・CLI・IoT | [flows/device-flow.md](./flows/device-flow.md) |

### 実装ガイド

| プラットフォーム | 参照ファイル |
|-----------------|-------------|
| React SPA | [implementation/spa-react.md](./implementation/spa-react.md) |
| Node.js サーバー | [implementation/server-nodejs.md](./implementation/server-nodejs.md) |
| モバイルアプリ | [implementation/mobile.md](./implementation/mobile.md) |

### その他

| トピック | 参照ファイル |
|---------|-------------|
| セキュリティベストプラクティス | [security/best-practices.md](./security/best-practices.md) |
| 共通パターン・例 | [examples/common-patterns.md](./examples/common-patterns.md) |

## Quick Decision Tree

```
認証が必要？
├─ ユーザーが関与する？
│   ├─ Yes → ブラウザ/リダイレクトが使える？
│   │   ├─ Yes → クライアントシークレットを安全に保存できる？
│   │   │   ├─ Yes → Authorization Code Flow
│   │   │   └─ No → Authorization Code + PKCE
│   │   └─ No → Device Authorization Flow
│   └─ No → Client Credentials Flow
```

## Core Concepts

### OAuth2 Roles

| 役割 | 説明 |
|-----|------|
| Resource Owner | データを所有するユーザー |
| Client | アクセスを要求するアプリケーション |
| Authorization Server | トークンを発行するサーバー |
| Resource Server | 保護されたリソースをホストするAPI |

### Token Types

| トークン | 用途 | 有効期間 |
|---------|------|---------|
| Access Token | リソースアクセス | 15分〜1時間 |
| Refresh Token | 新しいアクセストークン取得 | 日〜月単位 |
| ID Token (OIDC) | ユーザー識別情報 | 15分〜1時間 |

### Security Essentials

**必須:**
- HTTPS必須
- PKCE（公開クライアント）
- State パラメータ（CSRF防止）
- 厳格なリダイレクトURI検証

**禁止:**
- Implicit Flow（非推奨）
- localStorage へのトークン保存
- Resource Owner Password Credentials

## OIDC Discovery

認可サーバーの設定は `.well-known/openid-configuration` から自動取得可能:

```bash
GET https://auth.example.com/.well-known/openid-configuration
```

主要なエンドポイント:
- `authorization_endpoint` - 認可リクエスト先
- `token_endpoint` - トークン交換先
- `userinfo_endpoint` - ユーザー情報取得先
- `jwks_uri` - JWT検証用公開鍵

## Standard Scopes

| スコープ | 説明 |
|---------|------|
| `openid` | OIDC必須（ID Token取得） |
| `profile` | ユーザープロフィール情報 |
| `email` | メールアドレス |
| `address` | 住所情報 |
| `phone` | 電話番号 |
| `offline_access` | Refresh Token要求 |

## Resources

### 公式仕様
- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- [RFC 7636 - PKCE](https://tools.ietf.org/html/rfc7636)
- [RFC 6750 - Bearer Token](https://tools.ietf.org/html/rfc6750)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)

### セキュリティガイダンス
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [OAuth 2.0 for Browser-Based Apps](https://tools.ietf.org/html/draft-ietf-oauth-browser-based-apps)

## Version & Metadata

- **Skill Version**: 1.0.0
- **Last Updated**: January 2026
- **Category**: Authentication, Authorization, Security
