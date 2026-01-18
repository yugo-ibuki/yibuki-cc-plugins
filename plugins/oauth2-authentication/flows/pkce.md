# Authorization Code Flow with PKCE

SPA・モバイルアプリなど、クライアントシークレットを安全に保存できない公開クライアント向けのフロー。

## When to Use

- Single Page Applications (React, Vue, Angular)
- モバイルアプリケーション (iOS, Android, React Native)
- デスクトップアプリケーション
- クライアントシークレットを保存できない環境

## PKCE (Proof Key for Code Exchange)

認可コードの傍受攻撃を防ぐための拡張。

### Key Components

| 項目 | 説明 |
|-----|------|
| Code Verifier | 43-128文字のランダム文字列 |
| Code Challenge | Code Verifier の SHA256 ハッシュ（Base64URL） |
| Method | `S256`（推奨）または `plain` |

## Flow Steps

```
1. Client: code_verifier を生成
2. Client: code_challenge = SHA256(code_verifier) を計算
3. Client → Auth Server: 認可リクエスト + code_challenge
4. User: 認証・同意
5. Auth Server → Client: 認可コード
6. Client → Auth Server: トークンリクエスト + code_verifier
7. Auth Server: code_verifier を検証
8. Auth Server → Client: トークン発行
```

## Implementation

### PKCE Helper Functions

```javascript
function generateRandomString(length) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const values = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(values)
    .map(v => charset[v % charset.length])
    .join('');
}

async function generateCodeChallenge(codeVerifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return base64UrlEncode(digest);
}

function base64UrlEncode(buffer) {
  const bytes = new Uint8Array(buffer);
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

### Login Function

```javascript
async function login() {
  // Generate PKCE parameters
  const codeVerifier = generateRandomString(64);
  const codeChallenge = await generateCodeChallenge(codeVerifier);
  const state = generateRandomString(32);

  // Store for callback
  sessionStorage.setItem('code_verifier', codeVerifier);
  sessionStorage.setItem('oauth2_state', state);

  const params = new URLSearchParams({
    client_id: 'your_client_id',
    redirect_uri: window.location.origin + '/callback',
    response_type: 'code',
    scope: 'openid profile email',
    state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
  });

  window.location.href = `https://auth.example.com/authorize?${params}`;
}
```

### Callback Handler

```javascript
async function handleCallback(code, state) {
  // Validate state
  const savedState = sessionStorage.getItem('oauth2_state');
  if (state !== savedState) {
    throw new Error('Invalid state - possible CSRF attack');
  }

  // Get code verifier
  const codeVerifier = sessionStorage.getItem('code_verifier');
  if (!codeVerifier) {
    throw new Error('Code verifier not found');
  }

  // Exchange code for tokens
  const response = await fetch('https://auth.example.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: window.location.origin + '/callback',
      client_id: 'your_client_id',
      code_verifier: codeVerifier,  // PKCE: Send verifier
    }),
  });

  const tokens = await response.json();

  // Clean up
  sessionStorage.removeItem('code_verifier');
  sessionStorage.removeItem('oauth2_state');

  return tokens;
}
```

## Token Storage for SPAs

**推奨パターン:**

```javascript
// Access token: メモリのみ（React state, Redux, etc.）
const [accessToken, setAccessToken] = useState(null);

// Refresh token: Backend for Frontend (BFF) パターン
// → バックエンドで httpOnly cookie として管理
async function storeRefreshToken(refreshToken) {
  await fetch('/api/auth/store-token', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken }),
  });
}
```

**避けるべきパターン:**

```javascript
// ❌ localStorage - XSS脆弱性
localStorage.setItem('access_token', token);

// ❌ sessionStorage - 同様にXSS脆弱性
sessionStorage.setItem('access_token', token);
```

## Security Considerations

| 項目 | 実装 |
|-----|------|
| PKCE | 必須（S256 method） |
| State | 必須（CSRF防止） |
| Token Storage | メモリのみ（XSS対策） |
| Refresh Token | BFF経由でhttpOnly cookie |
| Client Secret | 使用しない |

## Related Files

- [SPA React Implementation](../implementation/spa-react.md) - 完全な実装例
- [Mobile Implementation](../implementation/mobile.md) - モバイル向け実装
- [Security Best Practices](../security/best-practices.md)
