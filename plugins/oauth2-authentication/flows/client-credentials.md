# Client Credentials Flow

バックエンドサービス間のマシン間（M2M）認証向けフロー。ユーザーコンテキストなし。

## When to Use

- バックエンドサービス間のAPI通信
- Cronジョブ・スケジュールタスク
- マイクロサービス間認証
- CI/CDパイプライン
- システムレベルの操作

## Characteristics

| 特徴 | 説明 |
|-----|------|
| ユーザー関与 | なし |
| リソースオーナー | クライアント自身 |
| Refresh Token | なし（新しいトークンを再取得） |
| トークンキャッシュ | 推奨 |

## Flow Steps

```
1. Client → Auth Server: client_id + client_secret
2. Auth Server: クライアント認証
3. Auth Server → Client: access_token
```

## Implementation (Node.js)

```javascript
class OAuth2Client {
  constructor(config) {
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.tokenEndpoint = config.tokenEndpoint;
    this.audience = config.audience;
    this.scopes = config.scopes || [];

    this.accessToken = null;
    this.tokenExpiry = null;
  }

  async getAccessToken() {
    // Return cached token if valid
    if (this.accessToken && Date.now() < this.tokenExpiry - 60000) {
      return this.accessToken;
    }

    // Request new token
    const response = await fetch(this.tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        audience: this.audience,
        scope: this.scopes.join(' '),
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to obtain access token');
    }

    const data = await response.json();

    // Cache token
    this.accessToken = data.access_token;
    this.tokenExpiry = Date.now() + (data.expires_in * 1000);

    return this.accessToken;
  }

  async callApi(endpoint, options = {}) {
    const token = await this.getAccessToken();

    const response = await fetch(endpoint, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      },
    });

    // Handle token expiration
    if (response.status === 401) {
      this.accessToken = null;
      const newToken = await this.getAccessToken();
      return fetch(endpoint, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`,
        },
      });
    }

    return response;
  }
}
```

### Usage

```javascript
const client = new OAuth2Client({
  clientId: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
  tokenEndpoint: 'https://auth.example.com/oauth/token',
  audience: 'https://api.example.com',
  scopes: ['read:data', 'write:data'],
});

// Make authenticated API calls
const response = await client.callApi('https://api.example.com/data');
const data = await response.json();
```

## Implementation (Python)

```python
import requests
from datetime import datetime, timedelta

class OAuth2Client:
    def __init__(self, client_id, client_secret, token_endpoint, audience=None, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint
        self.audience = audience
        self.scopes = scopes or []
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self):
        if self.access_token and datetime.now() < self.token_expiry - timedelta(minutes=1):
            return self.access_token

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        if self.audience:
            data['audience'] = self.audience
        if self.scopes:
            data['scope'] = ' '.join(self.scopes)

        response = requests.post(self.token_endpoint, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data['access_token']
        self.token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])

        return self.access_token

    def call_api(self, url, method='GET', **kwargs):
        token = self.get_access_token()
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {token}'

        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401:
            self.access_token = None
            token = self.get_access_token()
            headers['Authorization'] = f'Bearer {token}'
            response = requests.request(method, url, headers=headers, **kwargs)

        return response
```

## Security Considerations

| 項目 | 実装 |
|-----|------|
| クライアントシークレット | 環境変数で管理、コードにハードコードしない |
| トークンキャッシュ | 有効期限を考慮してキャッシュ |
| 接続プーリング | HTTP接続を再利用 |
| スコープ | 最小限の権限のみ要求 |

## Related Files

- [Server Implementation](../implementation/server-nodejs.md)
- [Security Best Practices](../security/best-practices.md)
