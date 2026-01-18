# Security Best Practices

OAuth2実装のセキュリティベストプラクティス。

## Token Security

### Storage Guidelines

| プラットフォーム | Access Token | Refresh Token |
|--------------|--------------|---------------|
| SPA | メモリのみ | httpOnly Cookie (BFF経由) |
| Server | セッション/Redis | セッション/Redis |
| Mobile | SecureStore/Keychain | SecureStore/Keychain |
| CLI | OS Keyring | OS Keyring |

### ❌ Never Do
```javascript
// DON'T: localStorage/sessionStorage にトークン保存
localStorage.setItem('access_token', token);  // XSS脆弱性

// DON'T: URL/クエリパラメータにトークン含める
window.location.href = `/api?token=${accessToken}`;  // ログ漏洩

// DON'T: グローバル変数に保存
window.accessToken = token;  // XSS脆弱性
```

### ✅ Do Instead
```javascript
// DO: メモリ内変数（クロージャ内）
const createTokenManager = () => {
  let accessToken = null;
  return {
    setToken: (token) => { accessToken = token; },
    getToken: () => accessToken,
    clearToken: () => { accessToken = null; },
  };
};

// DO: httpOnly Cookie（サーバー側で設定）
res.cookie('refresh_token', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 30 * 24 * 60 * 60 * 1000,
});
```

## PKCE Implementation

### Required for Public Clients
- SPA（シングルページアプリケーション）
- モバイルアプリ
- デスクトップアプリ
- CLIツール

### Code Verifier Requirements
```javascript
// 43-128文字のランダム文字列
// 使用可能文字: [A-Z] [a-z] [0-9] - . _ ~
function generateCodeVerifier(length = 64) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const values = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(values)
    .map(v => charset[v % charset.length])
    .join('');
}
```

### Code Challenge Generation
```javascript
// SHA-256ハッシュ → Base64URL エンコード
async function generateCodeChallenge(codeVerifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await crypto.subtle.digest('SHA-256', data);

  const bytes = new Uint8Array(digest);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }

  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}
```

## State Parameter

### CSRF Protection
```javascript
// 認可リクエスト前に生成・保存
const state = crypto.randomUUID();
sessionStorage.setItem('oauth2_state', state);

// コールバックで検証
const returnedState = urlParams.get('state');
const savedState = sessionStorage.getItem('oauth2_state');

if (returnedState !== savedState) {
  throw new Error('State mismatch - possible CSRF attack');
}

// 使用後は削除
sessionStorage.removeItem('oauth2_state');
```

## Redirect URI Security

### Validation Rules
```javascript
// サーバー側での検証
const allowedRedirectUris = [
  'https://app.example.com/auth/callback',
  'https://staging.example.com/auth/callback',
];

function validateRedirectUri(uri) {
  // 完全一致が必須
  if (!allowedRedirectUris.includes(uri)) {
    throw new Error('Invalid redirect URI');
  }

  // オープンリダイレクト防止
  const parsed = new URL(uri);
  if (parsed.hostname !== 'app.example.com' &&
      parsed.hostname !== 'staging.example.com') {
    throw new Error('Redirect URI domain not allowed');
  }
}
```

### Mobile Deep Links
```javascript
// カスタムスキーム（脆弱）
'com.yourapp://auth/callback'

// Universal Links / App Links（推奨）
'https://app.example.com/auth/callback'
// ※ apple-app-site-association / assetlinks.json が必要
```

## Token Validation

### JWT Verification
```javascript
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');

const client = jwksClient({
  jwksUri: 'https://auth.example.com/.well-known/jwks.json',
  cache: true,
  cacheMaxAge: 86400000, // 24時間
});

async function verifyToken(token) {
  const decoded = jwt.decode(token, { complete: true });
  if (!decoded) {
    throw new Error('Invalid token format');
  }

  const key = await client.getSigningKey(decoded.header.kid);
  const publicKey = key.getPublicKey();

  return jwt.verify(token, publicKey, {
    algorithms: ['RS256'],
    issuer: 'https://auth.example.com',
    audience: 'https://api.example.com',
    clockTolerance: 30, // 30秒の時刻ずれ許容
  });
}
```

### Required Claims Validation
```javascript
function validateClaims(payload) {
  const now = Math.floor(Date.now() / 1000);

  // 有効期限チェック
  if (payload.exp && payload.exp < now) {
    throw new Error('Token expired');
  }

  // 発行時刻チェック
  if (payload.iat && payload.iat > now + 30) {
    throw new Error('Token issued in the future');
  }

  // Not Before チェック
  if (payload.nbf && payload.nbf > now) {
    throw new Error('Token not yet valid');
  }

  // Issuer チェック
  if (payload.iss !== 'https://auth.example.com') {
    throw new Error('Invalid issuer');
  }

  // Audience チェック
  const validAudiences = ['https://api.example.com'];
  if (!validAudiences.includes(payload.aud)) {
    throw new Error('Invalid audience');
  }
}
```

## Refresh Token Security

### Rotation
```javascript
// サーバー側: リフレッシュ時に新しいトークンを発行
async function refreshTokens(refreshToken) {
  // 現在のリフレッシュトークンを無効化
  await invalidateRefreshToken(refreshToken);

  // 新しいトークンペアを生成
  const newAccessToken = generateAccessToken(user);
  const newRefreshToken = generateRefreshToken(user);

  // 新しいリフレッシュトークンを保存
  await saveRefreshToken(newRefreshToken, user.id);

  return { accessToken: newAccessToken, refreshToken: newRefreshToken };
}
```

### Revocation
```javascript
// ログアウト時のトークン無効化
async function logout(accessToken, refreshToken) {
  // リフレッシュトークンを無効化
  if (refreshToken) {
    await fetch('https://auth.example.com/oauth/revoke', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        token: refreshToken,
        token_type_hint: 'refresh_token',
        client_id: config.clientId,
      }),
    });
  }

  // アクセストークンも無効化（サポートされている場合）
  if (accessToken) {
    await fetch('https://auth.example.com/oauth/revoke', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        token: accessToken,
        token_type_hint: 'access_token',
        client_id: config.clientId,
      }),
    });
  }
}
```

## Client Secret Protection

### Server-Side Only
```javascript
// ❌ クライアントサイドに含めない
const config = {
  clientId: 'public_client_id',
  clientSecret: 'NEVER_DO_THIS', // 絶対にNG
};

// ✅ 環境変数で管理（サーバー側のみ）
const config = {
  clientId: process.env.OAUTH2_CLIENT_ID,
  clientSecret: process.env.OAUTH2_CLIENT_SECRET, // サーバー側のみ
};
```

## Error Handling

### Secure Error Messages
```javascript
// ❌ 詳細なエラー情報を露出しない
res.status(401).json({
  error: 'User not found in database table users where email = xxx@example.com'
});

// ✅ 一般的なエラーメッセージ
res.status(401).json({
  error: 'invalid_grant',
  error_description: 'The provided authorization grant is invalid'
});
```

### Error Logging
```javascript
// 詳細はサーバーログに記録
console.error('Token validation failed:', {
  error: error.message,
  tokenId: token.jti,
  userId: token.sub,
  timestamp: new Date().toISOString(),
});

// クライアントには一般的なエラーのみ
res.status(401).json({ error: 'Authentication failed' });
```

## HTTPS Requirements

### Enforce TLS
```javascript
// Express: HTTPS リダイレクト
app.use((req, res, next) => {
  if (req.header('x-forwarded-proto') !== 'https' && process.env.NODE_ENV === 'production') {
    return res.redirect(`https://${req.header('host')}${req.url}`);
  }
  next();
});

// HSTS ヘッダー設定
app.use((req, res, next) => {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  next();
});
```

## Security Headers

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://auth.example.com"],
      frameSrc: ["'none'"],
      objectSrc: ["'none'"],
    },
  },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));
```

## Checklist

### Implementation Checklist

- [ ] PKCE使用（公開クライアント）
- [ ] State パラメータ検証
- [ ] トークンをメモリ/セキュアストレージに保存
- [ ] localStorageにトークン保存していない
- [ ] リフレッシュトークンローテーション実装
- [ ] トークン無効化（ログアウト時）
- [ ] JWT署名検証
- [ ] Claims（exp, iss, aud）検証
- [ ] HTTPS強制
- [ ] セキュリティヘッダー設定
- [ ] エラーメッセージが情報漏洩しない
- [ ] リダイレクトURI完全一致検証

## Related Files

- [PKCE Flow](../flows/pkce.md)
- [SPA Implementation](../implementation/spa-react.md)
- [Server Implementation](../implementation/server-nodejs.md)
