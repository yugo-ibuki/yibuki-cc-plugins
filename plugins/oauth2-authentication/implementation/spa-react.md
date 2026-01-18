# SPA Implementation (React)

React SPAでのOAuth2 + PKCE実装の完全ガイド。

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    React SPA                        │
├─────────────────────────────────────────────────────┤
│  AuthContext          │  API Client                 │
│  ├─ user state        │  ├─ token management        │
│  ├─ login()           │  ├─ auto refresh            │
│  └─ logout()          │  └─ retry on 401            │
├─────────────────────────────────────────────────────┤
│  Token Storage: Memory only (NOT localStorage)      │
└─────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│ Auth Server     │      │ BFF / API       │
│ (PKCE flow)     │      │ (refresh token  │
│                 │      │  in httpOnly)   │
└─────────────────┘      └─────────────────┘
```

## Configuration

```javascript
// src/config/oauth2.js
export const oauth2Config = {
  clientId: import.meta.env.VITE_OAUTH2_CLIENT_ID,
  authorizationEndpoint: 'https://auth.example.com/oauth/authorize',
  tokenEndpoint: 'https://auth.example.com/oauth/token',
  redirectUri: window.location.origin + '/auth/callback',
  scopes: ['openid', 'profile', 'email'],
  audience: 'https://api.example.com',
};
```

## PKCE Utilities

```javascript
// src/utils/pkce.js
export function generateRandomString(length) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const values = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(values)
    .map(v => charset[v % charset.length])
    .join('');
}

export async function generateCodeChallenge(codeVerifier) {
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

## Auth Context

```javascript
// src/contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { oauth2Config } from '../config/oauth2';
import { generateRandomString, generateCodeChallenge } from '../utils/pkce';

const AuthContext = createContext(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize: check for existing session
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Try to refresh token via BFF
      const success = await tryRefresh();
      if (!success) {
        setLoading(false);
      }
    } catch {
      setLoading(false);
    }
  };

  const login = useCallback(async () => {
    const codeVerifier = generateRandomString(64);
    const codeChallenge = await generateCodeChallenge(codeVerifier);
    const state = generateRandomString(32);

    // Store PKCE params (sessionStorage OK for temporary PKCE data)
    sessionStorage.setItem('code_verifier', codeVerifier);
    sessionStorage.setItem('oauth2_state', state);

    const params = new URLSearchParams({
      client_id: oauth2Config.clientId,
      redirect_uri: oauth2Config.redirectUri,
      response_type: 'code',
      scope: oauth2Config.scopes.join(' '),
      state,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
    });

    window.location.href = `${oauth2Config.authorizationEndpoint}?${params}`;
  }, []);

  const handleCallback = useCallback(async (code, state) => {
    // Validate state
    const savedState = sessionStorage.getItem('oauth2_state');
    if (state !== savedState) {
      throw new Error('Invalid state - possible CSRF attack');
    }

    const codeVerifier = sessionStorage.getItem('code_verifier');
    if (!codeVerifier) {
      throw new Error('Code verifier not found');
    }

    // Exchange code for tokens
    const response = await fetch(oauth2Config.tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: oauth2Config.redirectUri,
        client_id: oauth2Config.clientId,
        code_verifier: codeVerifier,
      }),
    });

    if (!response.ok) {
      throw new Error('Token exchange failed');
    }

    const tokens = await response.json();

    // Store access token in memory
    setAccessToken(tokens.access_token);

    // Store refresh token via BFF (httpOnly cookie)
    if (tokens.refresh_token) {
      await fetch('/api/auth/store-token', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken: tokens.refresh_token }),
      });
    }

    // Fetch user info
    await fetchUserInfo(tokens.access_token);

    // Clean up
    sessionStorage.removeItem('code_verifier');
    sessionStorage.removeItem('oauth2_state');
  }, []);

  const fetchUserInfo = async (token) => {
    const response = await fetch('https://auth.example.com/oauth/userinfo', {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const userInfo = await response.json();
      setUser(userInfo);
      setLoading(false);
    }
  };

  const tryRefresh = async () => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        const tokens = await response.json();
        setAccessToken(tokens.access_token);
        await fetchUserInfo(tokens.access_token);
        return true;
      }
    } catch {
      // Refresh failed
    }
    return false;
  };

  const logout = useCallback(async () => {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    });

    setUser(null);
    setAccessToken(null);
  }, []);

  const value = {
    user,
    accessToken,
    loading,
    isAuthenticated: !!accessToken,
    login,
    logout,
    handleCallback,
    refreshToken: tryRefresh,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
```

## Callback Component

```javascript
// src/components/AuthCallback.jsx
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { handleCallback } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const errorParam = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    if (errorParam) {
      setError(errorDescription || errorParam);
      return;
    }

    if (code && state) {
      handleCallback(code, state)
        .then(() => navigate('/dashboard'))
        .catch((err) => setError(err.message));
    } else {
      setError('Missing authorization code or state');
    }
  }, [searchParams, handleCallback, navigate]);

  if (error) {
    return (
      <div className="auth-error">
        <h2>Authentication Failed</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')}>Return Home</button>
      </div>
    );
  }

  return (
    <div className="auth-loading">
      <h2>Completing authentication...</h2>
    </div>
  );
}
```

## Protected Route

```javascript
// src/components/ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
```

## API Client with Auto-Refresh

```javascript
// src/utils/apiClient.js
class ApiClient {
  constructor(getToken, refreshToken) {
    this.baseUrl = 'https://api.example.com';
    this.getToken = getToken;
    this.refreshToken = refreshToken;
  }

  async request(endpoint, options = {}) {
    let token = this.getToken();

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    // Auto-refresh on 401
    if (response.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        token = this.getToken();
        return fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
      throw new Error('Session expired');
    }

    return response;
  }

  async get(endpoint) {
    return this.request(endpoint);
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Usage with hook
export function useApiClient() {
  const { accessToken, refreshToken } = useAuth();

  return new ApiClient(
    () => accessToken,
    refreshToken
  );
}
```

## App Setup

```javascript
// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AuthCallback } from './components/AuthCallback';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { Dashboard } from './pages/Dashboard';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

## BFF Endpoints (Express)

```javascript
// server/auth.js - Backend for Frontend
const express = require('express');
const router = express.Router();

// Store refresh token in httpOnly cookie
router.post('/store-token', (req, res) => {
  const { refreshToken } = req.body;

  res.cookie('refresh_token', refreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
  });

  res.json({ success: true });
});

// Refresh access token
router.post('/refresh', async (req, res) => {
  const refreshToken = req.cookies.refresh_token;

  if (!refreshToken) {
    return res.status(401).json({ error: 'No refresh token' });
  }

  try {
    const response = await fetch('https://auth.example.com/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
        client_id: process.env.OAUTH2_CLIENT_ID,
      }),
    });

    const tokens = await response.json();

    // Update refresh token cookie if rotated
    if (tokens.refresh_token) {
      res.cookie('refresh_token', tokens.refresh_token, {
        httpOnly: true,
        secure: true,
        sameSite: 'strict',
        maxAge: 30 * 24 * 60 * 60 * 1000,
      });
    }

    res.json({ access_token: tokens.access_token });
  } catch {
    res.status(401).json({ error: 'Refresh failed' });
  }
});

// Logout
router.post('/logout', (req, res) => {
  res.clearCookie('refresh_token');
  res.json({ success: true });
});

module.exports = router;
```

## Related Files

- [PKCE Flow](../flows/pkce.md)
- [Security Best Practices](../security/best-practices.md)
