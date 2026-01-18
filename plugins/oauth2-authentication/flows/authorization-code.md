# Authorization Code Flow

サーバーサイドWebアプリケーション向けの最もセキュアなOAuth2フロー。

## When to Use

- 従来のサーバーサイドWebアプリケーション
- クライアントシークレットを安全に保存できる環境
- 最大限のセキュリティが必要な場合
- リフレッシュトークンが必要な場合

## Flow Steps

```
1. Client → Authorization Server: 認可リクエスト
   (client_id, redirect_uri, scope, state)

2. User → Authorization Server: 認証・同意

3. Authorization Server → Client: 認可コード
   (redirect_uri?code=xxx&state=xxx)

4. Client → Authorization Server: トークンリクエスト
   (code, client_secret, redirect_uri)

5. Authorization Server → Client: トークン発行
   (access_token, refresh_token, id_token)
```

## Implementation (Node.js + Express)

### Configuration

```javascript
const oauth2Config = {
  clientId: process.env.OAUTH2_CLIENT_ID,
  clientSecret: process.env.OAUTH2_CLIENT_SECRET,
  authorizationEndpoint: 'https://auth.example.com/oauth/authorize',
  tokenEndpoint: 'https://auth.example.com/oauth/token',
  redirectUri: 'https://yourapp.com/auth/callback',
  scopes: ['openid', 'profile', 'email'],
};
```

### Login Route

```javascript
const crypto = require('crypto');

app.get('/auth/login', (req, res) => {
  // Generate state for CSRF protection
  const state = crypto.randomBytes(32).toString('hex');
  req.session.oauth2State = state;

  const params = new URLSearchParams({
    client_id: oauth2Config.clientId,
    redirect_uri: oauth2Config.redirectUri,
    response_type: 'code',
    scope: oauth2Config.scopes.join(' '),
    state: state,
  });

  res.redirect(`${oauth2Config.authorizationEndpoint}?${params}`);
});
```

### Callback Route

```javascript
app.get('/auth/callback', async (req, res) => {
  const { code, state, error, error_description } = req.query;

  // Check for errors
  if (error) {
    console.error('Authorization error:', error, error_description);
    return res.redirect('/auth/error');
  }

  // Validate state (CSRF protection)
  if (state !== req.session.oauth2State) {
    return res.status(403).send('Invalid state parameter');
  }
  delete req.session.oauth2State;

  try {
    // Exchange code for tokens
    const response = await fetch(oauth2Config.tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: oauth2Config.redirectUri,
        client_id: oauth2Config.clientId,
        client_secret: oauth2Config.clientSecret,
      }),
    });

    const tokens = await response.json();

    // Store tokens in session
    req.session.accessToken = tokens.access_token;
    req.session.refreshToken = tokens.refresh_token;
    req.session.tokenExpiry = Date.now() + (tokens.expires_in * 1000);

    res.redirect('/dashboard');
  } catch (error) {
    console.error('Token exchange failed:', error);
    res.redirect('/auth/error');
  }
});
```

### Token Refresh

```javascript
async function refreshAccessToken(req) {
  if (!req.session.refreshToken) {
    throw new Error('No refresh token available');
  }

  const response = await fetch(oauth2Config.tokenEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: req.session.refreshToken,
      client_id: oauth2Config.clientId,
      client_secret: oauth2Config.clientSecret,
    }),
  });

  const tokens = await response.json();

  req.session.accessToken = tokens.access_token;
  req.session.tokenExpiry = Date.now() + (tokens.expires_in * 1000);

  if (tokens.refresh_token) {
    req.session.refreshToken = tokens.refresh_token;
  }

  return tokens.access_token;
}
```

### Auth Middleware

```javascript
async function requireAuth(req, res, next) {
  if (!req.session.accessToken) {
    return res.redirect('/auth/login');
  }

  // Check token expiry
  if (Date.now() > req.session.tokenExpiry - 60000) {
    try {
      await refreshAccessToken(req);
    } catch (error) {
      return res.redirect('/auth/login');
    }
  }

  next();
}
```

## Security Considerations

| 項目 | 実装 |
|-----|------|
| State パラメータ | 必須（CSRF防止） |
| HTTPS | 必須 |
| クライアントシークレット | サーバーサイドのみで使用 |
| トークン保存 | セッション（httpOnly cookie） |
| リダイレクトURI | 厳格な完全一致検証 |

## Related Files

- [PKCE Flow](./pkce.md) - 公開クライアント向け
- [Server Implementation](../implementation/server-nodejs.md) - 詳細な実装例
