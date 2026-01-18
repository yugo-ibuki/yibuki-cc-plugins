# Device Authorization Flow

入力機能が制限されたデバイス向けのフロー。

## When to Use

- スマートTV・ストリーミングデバイス
- IoTデバイス（キーボードなし）
- CLIツール・ターミナルアプリケーション
- ゲームコンソール
- 入力が困難なデバイス全般

## Flow Steps

```
1. Device → Auth Server: デバイスコードリクエスト
   (client_id, scope)

2. Auth Server → Device: device_code, user_code, verification_uri

3. Device → User: URLとユーザーコードを表示
   "https://auth.example.com/device にアクセスして
    コード ABC-123 を入力してください"

4. User → 別デバイス: URLにアクセスしてコード入力・認証

5. Device → Auth Server: トークンポーリング
   (device_code を使って定期的に確認)

6. Auth Server → Device: access_token (認証完了時)
```

## Implementation

### Step 1: Request Device Code

```javascript
async function requestDeviceCode() {
  const response = await fetch('https://auth.example.com/oauth/device/code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: 'your_client_id',
      scope: 'openid profile email',
    }),
  });

  return response.json();
  // Returns:
  // {
  //   device_code: "xxx",
  //   user_code: "ABC-123",
  //   verification_uri: "https://auth.example.com/device",
  //   verification_uri_complete: "https://auth.example.com/device?user_code=ABC-123",
  //   expires_in: 1800,
  //   interval: 5
  // }
}
```

### Step 2: Display Instructions

```javascript
function displayInstructions(deviceCodeResponse) {
  console.log('\n========================================');
  console.log('デバイス認証が必要です');
  console.log('========================================');
  console.log(`\n1. ブラウザで以下のURLにアクセス:`);
  console.log(`   ${deviceCodeResponse.verification_uri}`);
  console.log(`\n2. 以下のコードを入力:`);
  console.log(`   ${deviceCodeResponse.user_code}`);
  console.log('\n認証が完了するまでお待ちください...\n');

  // QRコード表示も可能
  if (deviceCodeResponse.verification_uri_complete) {
    // QRコードライブラリでQRコード生成
    displayQRCode(deviceCodeResponse.verification_uri_complete);
  }
}
```

### Step 3: Poll for Token

```javascript
async function pollForToken(deviceCode, interval, expiresIn) {
  const startTime = Date.now();
  const timeout = expiresIn * 1000;

  while (Date.now() - startTime < timeout) {
    await sleep(interval * 1000);

    try {
      const response = await fetch('https://auth.example.com/oauth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
          device_code: deviceCode,
          client_id: 'your_client_id',
        }),
      });

      const data = await response.json();

      if (response.ok) {
        return data; // Success: { access_token, refresh_token, ... }
      }

      switch (data.error) {
        case 'authorization_pending':
          // User hasn't completed authorization yet
          continue;
        case 'slow_down':
          // Increase polling interval
          interval += 5;
          continue;
        case 'expired_token':
          throw new Error('Device code expired');
        case 'access_denied':
          throw new Error('User denied authorization');
        default:
          throw new Error(`Unknown error: ${data.error}`);
      }
    } catch (error) {
      if (error.message.includes('expired') || error.message.includes('denied')) {
        throw error;
      }
      // Network error, continue polling
      continue;
    }
  }

  throw new Error('Device code expired');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Complete Flow

```javascript
async function deviceLogin() {
  try {
    // Step 1: Get device code
    const deviceCodeResponse = await requestDeviceCode();

    // Step 2: Display instructions to user
    displayInstructions(deviceCodeResponse);

    // Step 3: Poll for token
    const tokens = await pollForToken(
      deviceCodeResponse.device_code,
      deviceCodeResponse.interval,
      deviceCodeResponse.expires_in
    );

    console.log('認証成功!');
    return tokens;
  } catch (error) {
    console.error('認証失敗:', error.message);
    throw error;
  }
}
```

## CLI Tool Example

```javascript
#!/usr/bin/env node

const { program } = require('commander');

program
  .command('login')
  .description('Authenticate with the service')
  .action(async () => {
    try {
      const tokens = await deviceLogin();

      // Store tokens securely
      await saveTokensToConfig(tokens);

      console.log('ログイン完了。CLIを使用できます。');
    } catch (error) {
      console.error('ログインに失敗しました:', error.message);
      process.exit(1);
    }
  });

program.parse();
```

## Error Handling

| エラーコード | 意味 | 対応 |
|-------------|------|------|
| `authorization_pending` | ユーザーがまだ認証していない | ポーリング継続 |
| `slow_down` | ポーリング頻度が高すぎる | interval を増やす |
| `expired_token` | デバイスコードが期限切れ | 最初からやり直し |
| `access_denied` | ユーザーが拒否 | エラー表示して終了 |

## Security Considerations

| 項目 | 実装 |
|-----|------|
| ポーリング間隔 | サーバー指定の interval を尊重 |
| タイムアウト | expires_in を超えたら停止 |
| ユーザーコード | 読みやすい形式（例: ABC-123） |
| トークン保存 | OSのセキュアストレージを使用 |

## Related Files

- [Security Best Practices](../security/best-practices.md)
