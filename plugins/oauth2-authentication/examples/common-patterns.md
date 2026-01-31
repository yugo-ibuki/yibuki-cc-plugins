# Common Patterns

OAuth2実装でよく使われるパターン集。

## Token Management Patterns

### In-Memory Token Manager

```javascript
// tokenManager.js
export function createTokenManager() {
  let accessToken = null;
  let tokenExpiry = null;

  return {
    setToken(token, expiresIn) {
      accessToken = token;
      tokenExpiry = Date.now() + expiresIn * 1000;
    },

    getToken() {
      return accessToken;
    },

    isExpired() {
      if (!tokenExpiry) return true;
      // 5分前に期限切れとみなす
      return Date.now() > tokenExpiry - 300000;
    },

    clear() {
      accessToken = null;
      tokenExpiry = null;
    },
  };
}
```

### Auto-Refresh Pattern

```javascript
// apiClient.js
class ApiClient {
  constructor(tokenManager, refreshFn) {
    this.tokenManager = tokenManager;
    this.refreshFn = refreshFn;
    this.refreshPromise = null;
  }

  async request(url, options = {}) {
    // 期限切れならリフレッシュ
    if (this.tokenManager.isExpired()) {
      await this.ensureValidToken();
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${this.tokenManager.getToken()}`,
      },
    });

    // 401ならリフレッシュして再試行
    if (response.status === 401) {
      await this.ensureValidToken();
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${this.tokenManager.getToken()}`,
        },
      });
    }

    return response;
  }

  // 同時リフレッシュを防ぐ
  async ensureValidToken() {
    if (!this.refreshPromise) {
      this.refreshPromise = this.refreshFn()
        .finally(() => { this.refreshPromise = null; });
    }
    return this.refreshPromise;
  }
}
```

## Authentication Flow Patterns

### Login with Redirect

```javascript
// auth.js
export function initiateLogin(returnUrl = window.location.href) {
  // 現在のURLを保存
  sessionStorage.setItem('auth_return_url', returnUrl);

  // PKCE パラメータ生成
  const codeVerifier = generateRandomString(64);
  const state = generateRandomString(32);

  sessionStorage.setItem('code_verifier', codeVerifier);
  sessionStorage.setItem('oauth2_state', state);

  // 認可サーバーにリダイレクト
  const authUrl = buildAuthUrl({ codeVerifier, state });
  window.location.href = authUrl;
}

export function getReturnUrl() {
  const url = sessionStorage.getItem('auth_return_url') || '/';
  sessionStorage.removeItem('auth_return_url');
  return url;
}
```

### Silent Token Renewal (iframe)

```javascript
// silentRenew.js
export function silentRenew() {
  return new Promise((resolve, reject) => {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';

    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error('Silent renewal timeout'));
    }, 10000);

    function cleanup() {
      clearTimeout(timeout);
      window.removeEventListener('message', handleMessage);
      iframe.remove();
    }

    function handleMessage(event) {
      if (event.origin !== window.location.origin) return;
      if (event.data.type !== 'auth_callback') return;

      cleanup();

      if (event.data.error) {
        reject(new Error(event.data.error));
      } else {
        resolve(event.data.tokens);
      }
    }

    window.addEventListener('message', handleMessage);

    // prompt=none で認可リクエスト
    const authUrl = buildAuthUrl({ prompt: 'none' });
    iframe.src = authUrl;
    document.body.appendChild(iframe);
  });
}
```

## Protected Route Patterns

### React Router Protection

```javascript
// ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

export function ProtectedRoute({ children, requiredScopes = [] }) {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // スコープチェック
  if (requiredScopes.length > 0) {
    const userScopes = user?.scopes || [];
    const hasAllScopes = requiredScopes.every(s => userScopes.includes(s));

    if (!hasAllScopes) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
}

// 使用例
<Route
  path="/admin"
  element={
    <ProtectedRoute requiredScopes={['admin:read', 'admin:write']}>
      <AdminDashboard />
    </ProtectedRoute>
  }
/>
```

### Express Middleware

```javascript
// authMiddleware.js
function requireAuth(req, res, next) {
  if (!req.session?.accessToken) {
    if (req.xhr || req.headers.accept?.includes('application/json')) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    return res.redirect(`/auth/login?returnTo=${encodeURIComponent(req.originalUrl)}`);
  }
  next();
}

function requireScopes(...scopes) {
  return (req, res, next) => {
    const tokenScopes = req.session?.scopes || [];
    const hasAll = scopes.every(s => tokenScopes.includes(s));

    if (!hasAll) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

// 使用例
router.get('/admin/users', requireAuth, requireScopes('admin:read'), getUsers);
```

### Role-Based Access Control

```javascript
// roleMiddleware.js
function requireRole(role) {
  return (req, res, next) => {
    if (!req.user?.roles?.includes(role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

// 複数ロールのいずれかを要求
function requireAnyRole(...roles) {
  return (req, res, next) => {
    const userRoles = req.user?.roles || [];
    const hasAnyRole = roles.some(role => userRoles.includes(role));

    if (!hasAnyRole) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

// 使用例
router.delete('/api/users/:id', requireAuth, requireRole('admin'), deleteUser);
router.get('/api/reports', requireAuth, requireAnyRole('admin', 'manager'), getReports);
```

## Error Handling Patterns

### Centralized Error Handler

```javascript
// errorHandler.js
export class AuthError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

export function handleAuthError(error) {
  switch (error.code) {
    case 'token_expired':
      // リフレッシュ試行
      return refreshAndRetry();

    case 'invalid_grant':
      // 再ログインが必要
      clearTokens();
      redirectToLogin();
      break;

    case 'insufficient_scope':
      // 権限不足
      showPermissionDenied();
      break;

    case 'network_error':
      // ネットワークエラー
      showRetryPrompt();
      break;

    default:
      // 一般的なエラー
      showGenericError();
  }
}
```

### Retry with Exponential Backoff

```javascript
// retry.js
async function retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // 認証エラーはリトライしない
      if (error.status === 401 || error.status === 403) {
        throw error;
      }

      // 最後の試行ならエラーを投げる
      if (attempt === maxRetries - 1) {
        throw error;
      }

      // 指数バックオフで待機
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}
```

## Session Management Patterns

### Session Timeout Warning

```javascript
// sessionManager.js
export function createSessionManager(options) {
  const { warningTime = 5 * 60 * 1000, onWarning, onTimeout } = options;
  let timeoutId;
  let warningId;

  function resetTimers(expiresIn) {
    clearTimeout(timeoutId);
    clearTimeout(warningId);

    const expiryMs = expiresIn * 1000;

    // 警告タイマー
    warningId = setTimeout(() => {
      onWarning?.(warningTime / 1000);
    }, expiryMs - warningTime);

    // タイムアウトタイマー
    timeoutId = setTimeout(() => {
      onTimeout?.();
    }, expiryMs);
  }

  function clear() {
    clearTimeout(timeoutId);
    clearTimeout(warningId);
  }

  return { resetTimers, clear };
}

// 使用例
const sessionManager = createSessionManager({
  warningTime: 5 * 60 * 1000, // 5分前
  onWarning: (seconds) => {
    showModal(`セッションが${seconds}秒後に期限切れになります。継続しますか？`);
  },
  onTimeout: () => {
    logout();
    redirectToLogin();
  },
});
```

### Multi-Tab Synchronization

```javascript
// tabSync.js
const AUTH_CHANNEL = 'auth_sync';

export function setupTabSync(authStore) {
  const channel = new BroadcastChannel(AUTH_CHANNEL);

  // 他のタブからのメッセージを受信
  channel.addEventListener('message', (event) => {
    switch (event.data.type) {
      case 'LOGIN':
        authStore.setUser(event.data.user);
        break;
      case 'LOGOUT':
        authStore.clear();
        window.location.href = '/login';
        break;
      case 'TOKEN_REFRESH':
        authStore.setToken(event.data.token);
        break;
    }
  });

  // 認証状態変更を他のタブに通知
  return {
    notifyLogin: (user) => channel.postMessage({ type: 'LOGIN', user }),
    notifyLogout: () => channel.postMessage({ type: 'LOGOUT' }),
    notifyRefresh: (token) => channel.postMessage({ type: 'TOKEN_REFRESH', token }),
  };
}
```

## API Integration Patterns

### Axios Interceptor

```javascript
// axiosConfig.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.example.com',
});

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  failedQueue = [];
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        logout();
        throw refreshError;
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Fetch Wrapper

```javascript
// fetchWithAuth.js
export async function fetchWithAuth(url, options = {}) {
  const token = await getValidToken();

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (response.status === 401) {
    // トークンリフレッシュして再試行
    const newToken = await refreshAccessToken();
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${newToken}`,
        'Content-Type': 'application/json',
      },
    });
  }

  return response;
}

// ヘルパー関数
export const api = {
  get: (url) => fetchWithAuth(url),
  post: (url, data) => fetchWithAuth(url, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  put: (url, data) => fetchWithAuth(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (url) => fetchWithAuth(url, { method: 'DELETE' }),
};
```

## Testing Patterns

### Mock Auth Provider

```javascript
// mockAuth.js
export function createMockAuthProvider(initialState = {}) {
  return {
    user: initialState.user || null,
    isAuthenticated: !!initialState.user,
    loading: false,
    login: jest.fn(),
    logout: jest.fn(),
    getValidToken: jest.fn().mockResolvedValue('mock_token'),
  };
}

// テストでの使用
test('displays user profile when authenticated', () => {
  const mockAuth = createMockAuthProvider({
    user: { name: 'Test User', email: 'test@example.com' },
  });

  render(
    <AuthContext.Provider value={mockAuth}>
      <Profile />
    </AuthContext.Provider>
  );

  expect(screen.getByText('Test User')).toBeInTheDocument();
});
```

### JWT Test Utilities

```javascript
// testUtils.js
import jwt from 'jsonwebtoken';

export function createTestToken(claims = {}, options = {}) {
  const payload = {
    sub: 'user123',
    iss: 'https://auth.example.com',
    aud: 'https://api.example.com',
    exp: Math.floor(Date.now() / 1000) + 3600,
    iat: Math.floor(Date.now() / 1000),
    ...claims,
  };

  return jwt.sign(payload, options.secret || 'test_secret', {
    algorithm: options.algorithm || 'HS256',
  });
}

export function createExpiredToken(claims = {}) {
  return createTestToken({
    ...claims,
    exp: Math.floor(Date.now() / 1000) - 3600,
  });
}
```

## Related Files

- [Security Best Practices](../security/best-practices.md)
- [SPA Implementation](../implementation/spa-react.md)
- [Server Implementation](../implementation/server-nodejs.md)
