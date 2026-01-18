# Mobile Implementation

iOS/Android/React Nativeでのモバイルアプリ向けOAuth2 + PKCE実装ガイド。

## Security Considerations for Mobile

| 項目 | 推奨 |
|-----|------|
| フロー | Authorization Code + PKCE（必須） |
| Client Secret | 使用しない（公開クライアント） |
| トークン保存 | プラットフォームのセキュアストレージ |
| リダイレクト | カスタムURLスキームまたはUniversal Links |

## React Native Implementation

### Dependencies

```bash
npm install expo-secure-store expo-auth-session expo-crypto expo-web-browser
```

### PKCE Utilities

```javascript
// src/utils/pkce.js
import * as Crypto from 'expo-crypto';

export function generateRandomString(length) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const randomBytes = Crypto.getRandomBytes(length);
  return Array.from(randomBytes)
    .map(b => charset[b % charset.length])
    .join('');
}

export async function generateCodeChallenge(codeVerifier) {
  const digest = await Crypto.digestStringAsync(
    Crypto.CryptoDigestAlgorithm.SHA256,
    codeVerifier,
    { encoding: Crypto.CryptoEncoding.BASE64 }
  );
  // Convert Base64 to Base64URL
  return digest
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}
```

### Secure Token Storage

```javascript
// src/utils/tokenStorage.js
import * as SecureStore from 'expo-secure-store';

const KEYS = {
  ACCESS_TOKEN: 'oauth2_access_token',
  REFRESH_TOKEN: 'oauth2_refresh_token',
  TOKEN_EXPIRY: 'oauth2_token_expiry',
  USER: 'oauth2_user',
};

export async function saveTokens(tokens) {
  await Promise.all([
    SecureStore.setItemAsync(KEYS.ACCESS_TOKEN, tokens.access_token),
    SecureStore.setItemAsync(KEYS.REFRESH_TOKEN, tokens.refresh_token || ''),
    SecureStore.setItemAsync(KEYS.TOKEN_EXPIRY, String(Date.now() + tokens.expires_in * 1000)),
  ]);
}

export async function getAccessToken() {
  return SecureStore.getItemAsync(KEYS.ACCESS_TOKEN);
}

export async function getRefreshToken() {
  return SecureStore.getItemAsync(KEYS.REFRESH_TOKEN);
}

export async function isTokenExpired() {
  const expiry = await SecureStore.getItemAsync(KEYS.TOKEN_EXPIRY);
  if (!expiry) return true;
  return Date.now() > parseInt(expiry);
}

export async function saveUser(user) {
  await SecureStore.setItemAsync(KEYS.USER, JSON.stringify(user));
}

export async function getUser() {
  const user = await SecureStore.getItemAsync(KEYS.USER);
  return user ? JSON.parse(user) : null;
}

export async function clearAll() {
  await Promise.all(Object.values(KEYS).map(key => SecureStore.deleteItemAsync(key)));
}
```

### Auth Context

```javascript
// src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import { makeRedirectUri } from 'expo-auth-session';
import { generateRandomString, generateCodeChallenge } from '../utils/pkce';
import * as tokenStorage from '../utils/tokenStorage';

const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

const config = {
  clientId: 'your_client_id',
  authorizationEndpoint: 'https://auth.example.com/oauth/authorize',
  tokenEndpoint: 'https://auth.example.com/oauth/token',
  redirectUri: makeRedirectUri({
    scheme: 'com.yourapp',
    path: 'auth/callback',
  }),
  scopes: ['openid', 'profile', 'email'],
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pkceState, setPkceState] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const savedUser = await tokenStorage.getUser();
      const isExpired = await tokenStorage.isTokenExpired();

      if (savedUser && !isExpired) {
        setUser(savedUser);
      } else if (savedUser) {
        // Try refresh
        await refreshAccessToken();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      // Generate PKCE parameters
      const codeVerifier = generateRandomString(64);
      const codeChallenge = await generateCodeChallenge(codeVerifier);
      const state = generateRandomString(32);

      // Store for callback
      setPkceState({ codeVerifier, state });

      const params = new URLSearchParams({
        client_id: config.clientId,
        redirect_uri: config.redirectUri,
        response_type: 'code',
        scope: config.scopes.join(' '),
        state,
        code_challenge: codeChallenge,
        code_challenge_method: 'S256',
      });

      const authUrl = `${config.authorizationEndpoint}?${params}`;

      // Open browser for authentication
      const result = await WebBrowser.openAuthSessionAsync(
        authUrl,
        config.redirectUri
      );

      if (result.type === 'success') {
        const url = new URL(result.url);
        const code = url.searchParams.get('code');
        const returnedState = url.searchParams.get('state');

        await handleCallback(code, returnedState, codeVerifier, state);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const handleCallback = async (code, returnedState, codeVerifier, originalState) => {
    // Validate state
    if (returnedState !== originalState) {
      throw new Error('Invalid state - possible CSRF attack');
    }

    // Exchange code for tokens
    const response = await fetch(config.tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: config.redirectUri,
        client_id: config.clientId,
        code_verifier: codeVerifier,
      }),
    });

    if (!response.ok) {
      throw new Error('Token exchange failed');
    }

    const tokens = await response.json();

    // Save tokens securely
    await tokenStorage.saveTokens(tokens);

    // Fetch user info
    const userInfo = await fetchUserInfo(tokens.access_token);
    await tokenStorage.saveUser(userInfo);
    setUser(userInfo);

    // Clear PKCE state
    setPkceState(null);
  };

  const fetchUserInfo = async (accessToken) => {
    const response = await fetch('https://auth.example.com/oauth/userinfo', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }

    return response.json();
  };

  const refreshAccessToken = async () => {
    try {
      const refreshToken = await tokenStorage.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token');
      }

      const response = await fetch(config.tokenEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          refresh_token: refreshToken,
          client_id: config.clientId,
        }),
      });

      if (!response.ok) {
        throw new Error('Refresh failed');
      }

      const tokens = await response.json();
      await tokenStorage.saveTokens(tokens);

      return tokens.access_token;
    } catch (error) {
      // Refresh failed, clear tokens
      await logout();
      throw error;
    }
  };

  const logout = async () => {
    await tokenStorage.clearAll();
    setUser(null);
  };

  const getValidToken = async () => {
    const isExpired = await tokenStorage.isTokenExpired();
    if (isExpired) {
      return refreshAccessToken();
    }
    return tokenStorage.getAccessToken();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
        getValidToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
```

### API Client Hook

```javascript
// src/hooks/useApiClient.js
import { useAuth } from '../contexts/AuthContext';

export function useApiClient() {
  const { getValidToken, logout } = useAuth();

  const request = async (endpoint, options = {}) => {
    try {
      const token = await getValidToken();

      const response = await fetch(`https://api.example.com${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        await logout();
        throw new Error('Session expired');
      }

      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  };

  return {
    get: (endpoint) => request(endpoint),
    post: (endpoint, data) => request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    put: (endpoint, data) => request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (endpoint) => request(endpoint, { method: 'DELETE' }),
  };
}
```

## iOS Native (Swift)

### Keychain Storage

```swift
// KeychainHelper.swift
import Security

class KeychainHelper {
    static let shared = KeychainHelper()

    func save(_ data: Data, service: String, account: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    func read(service: String, account: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        return result as? Data
    }

    func delete(service: String, account: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

## Android Native (Kotlin)

### EncryptedSharedPreferences

```kotlin
// TokenStorage.kt
import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class TokenStorage(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs = EncryptedSharedPreferences.create(
        context,
        "oauth2_tokens",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveAccessToken(token: String) {
        prefs.edit().putString("access_token", token).apply()
    }

    fun getAccessToken(): String? {
        return prefs.getString("access_token", null)
    }

    fun saveRefreshToken(token: String) {
        prefs.edit().putString("refresh_token", token).apply()
    }

    fun getRefreshToken(): String? {
        return prefs.getString("refresh_token", null)
    }

    fun clear() {
        prefs.edit().clear().apply()
    }
}
```

## Redirect URI Configuration

### Custom URL Scheme

```
# iOS Info.plist
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>com.yourapp</string>
        </array>
    </dict>
</array>

# Android AndroidManifest.xml
<activity android:name=".AuthCallbackActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="com.yourapp" android:host="auth" android:path="/callback"/>
    </intent-filter>
</activity>
```

### Universal Links / App Links

推奨: カスタムスキームより安全

```
# iOS: apple-app-site-association
{
  "applinks": {
    "apps": [],
    "details": [{
      "appID": "TEAMID.com.yourapp",
      "paths": ["/auth/callback"]
    }]
  }
}

# Android: assetlinks.json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.yourapp",
    "sha256_cert_fingerprints": ["..."]
  }
}]
```

## Related Files

- [PKCE Flow](../flows/pkce.md)
- [Security Best Practices](../security/best-practices.md)
