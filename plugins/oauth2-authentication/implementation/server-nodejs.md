# Server-Side Implementation (Node.js)

Node.js + ExpressでのOAuth2実装ガイド。

## Project Structure

```
src/
├── config/
│   └── oauth2.js
├── middleware/
│   └── auth.js
├── routes/
│   └── auth.js
├── services/
│   └── tokenService.js
└── app.js
```

## Configuration

```javascript
// src/config/oauth2.js
module.exports = {
  clientId: process.env.OAUTH2_CLIENT_ID,
  clientSecret: process.env.OAUTH2_CLIENT_SECRET,
  authorizationEndpoint: 'https://auth.example.com/oauth/authorize',
  tokenEndpoint: 'https://auth.example.com/oauth/token',
  userInfoEndpoint: 'https://auth.example.com/oauth/userinfo',
  jwksUri: 'https://auth.example.com/.well-known/jwks.json',
  redirectUri: process.env.OAUTH2_REDIRECT_URI,
  scopes: ['openid', 'profile', 'email'],
};
```

## Session Setup

```javascript
// src/app.js
const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

const app = express();

// Redis client for session storage
const redisClient = createClient({ url: process.env.REDIS_URL });
redisClient.connect();

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
    sameSite: 'lax',
  },
}));

app.use('/auth', require('./routes/auth'));
```

## Auth Routes

```javascript
// src/routes/auth.js
const express = require('express');
const crypto = require('crypto');
const oauth2Config = require('../config/oauth2');
const tokenService = require('../services/tokenService');

const router = express.Router();

// Login - redirect to authorization server
router.get('/login', (req, res) => {
  const state = crypto.randomBytes(32).toString('hex');
  req.session.oauth2State = state;

  // Store return URL
  if (req.query.returnTo) {
    req.session.returnTo = req.query.returnTo;
  }

  const params = new URLSearchParams({
    client_id: oauth2Config.clientId,
    redirect_uri: oauth2Config.redirectUri,
    response_type: 'code',
    scope: oauth2Config.scopes.join(' '),
    state,
  });

  res.redirect(`${oauth2Config.authorizationEndpoint}?${params}`);
});

// Callback - exchange code for tokens
router.get('/callback', async (req, res) => {
  const { code, state, error, error_description } = req.query;

  // Handle errors
  if (error) {
    console.error('Authorization error:', error, error_description);
    return res.redirect('/auth/error?message=' + encodeURIComponent(error_description || error));
  }

  // Validate state
  if (state !== req.session.oauth2State) {
    console.error('State mismatch');
    return res.status(403).send('Invalid state parameter');
  }
  delete req.session.oauth2State;

  try {
    // Exchange code for tokens
    const tokens = await tokenService.exchangeCode(code);

    // Store tokens in session
    req.session.accessToken = tokens.access_token;
    req.session.refreshToken = tokens.refresh_token;
    req.session.tokenExpiry = Date.now() + (tokens.expires_in * 1000);

    // Fetch and store user info
    if (tokens.id_token || tokens.access_token) {
      const userInfo = await tokenService.getUserInfo(tokens.access_token);
      req.session.user = userInfo;
    }

    // Redirect to original destination or dashboard
    const returnTo = req.session.returnTo || '/dashboard';
    delete req.session.returnTo;
    res.redirect(returnTo);
  } catch (error) {
    console.error('Token exchange failed:', error);
    res.redirect('/auth/error?message=Authentication failed');
  }
});

// Logout
router.post('/logout', async (req, res) => {
  // Revoke tokens if possible
  if (req.session.accessToken) {
    try {
      await tokenService.revokeToken(req.session.accessToken);
    } catch (error) {
      console.error('Token revocation failed:', error);
    }
  }

  // Destroy session
  req.session.destroy((err) => {
    if (err) {
      console.error('Session destruction failed:', err);
    }
    res.redirect('/');
  });
});

// Get current user
router.get('/me', (req, res) => {
  if (!req.session.user) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  res.json(req.session.user);
});

module.exports = router;
```

## Token Service

```javascript
// src/services/tokenService.js
const oauth2Config = require('../config/oauth2');

async function exchangeCode(code) {
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

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error_description || 'Token exchange failed');
  }

  return response.json();
}

async function refreshToken(refreshToken) {
  const response = await fetch(oauth2Config.tokenEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: oauth2Config.clientId,
      client_secret: oauth2Config.clientSecret,
    }),
  });

  if (!response.ok) {
    throw new Error('Token refresh failed');
  }

  return response.json();
}

async function getUserInfo(accessToken) {
  const response = await fetch(oauth2Config.userInfoEndpoint, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user info');
  }

  return response.json();
}

async function revokeToken(token) {
  await fetch('https://auth.example.com/oauth/revoke', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      token,
      client_id: oauth2Config.clientId,
      client_secret: oauth2Config.clientSecret,
    }),
  });
}

module.exports = {
  exchangeCode,
  refreshToken,
  getUserInfo,
  revokeToken,
};
```

## Auth Middleware

```javascript
// src/middleware/auth.js
const tokenService = require('../services/tokenService');

// Require authentication
function requireAuth(req, res, next) {
  if (!req.session.accessToken) {
    if (req.xhr || req.headers.accept?.includes('application/json')) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    return res.redirect('/auth/login?returnTo=' + encodeURIComponent(req.originalUrl));
  }
  next();
}

// Auto-refresh token if needed
async function refreshTokenIfNeeded(req, res, next) {
  if (!req.session.accessToken) {
    return next();
  }

  // Check if token needs refresh (5 minutes before expiry)
  const shouldRefresh = Date.now() > req.session.tokenExpiry - 300000;

  if (shouldRefresh && req.session.refreshToken) {
    try {
      const tokens = await tokenService.refreshToken(req.session.refreshToken);

      req.session.accessToken = tokens.access_token;
      req.session.tokenExpiry = Date.now() + (tokens.expires_in * 1000);

      if (tokens.refresh_token) {
        req.session.refreshToken = tokens.refresh_token;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear session on refresh failure
      delete req.session.accessToken;
      delete req.session.refreshToken;
    }
  }

  next();
}

// Require specific scopes
function requireScopes(...requiredScopes) {
  return (req, res, next) => {
    const tokenScopes = req.session.scopes || [];
    const hasAllScopes = requiredScopes.every(scope => tokenScopes.includes(scope));

    if (!hasAllScopes) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

module.exports = {
  requireAuth,
  refreshTokenIfNeeded,
  requireScopes,
};
```

## Protected Routes Example

```javascript
// src/routes/api.js
const express = require('express');
const { requireAuth, refreshTokenIfNeeded } = require('../middleware/auth');

const router = express.Router();

// Apply middleware to all routes
router.use(refreshTokenIfNeeded);
router.use(requireAuth);

router.get('/profile', (req, res) => {
  res.json(req.session.user);
});

router.get('/data', async (req, res) => {
  // Use access token to call external API
  const response = await fetch('https://api.example.com/data', {
    headers: {
      Authorization: `Bearer ${req.session.accessToken}`,
    },
  });

  const data = await response.json();
  res.json(data);
});

module.exports = router;
```

## JWT Validation (for API servers)

```javascript
// src/middleware/validateJwt.js
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');
const oauth2Config = require('../config/oauth2');

const client = jwksClient({
  jwksUri: oauth2Config.jwksUri,
  cache: true,
  cacheMaxAge: 86400000, // 24 hours
});

async function getSigningKey(kid) {
  const key = await client.getSigningKey(kid);
  return key.getPublicKey();
}

async function validateJwt(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid authorization header' });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.decode(token, { complete: true });
    if (!decoded) {
      throw new Error('Invalid token');
    }

    const publicKey = await getSigningKey(decoded.header.kid);

    const payload = jwt.verify(token, publicKey, {
      algorithms: ['RS256'],
      issuer: 'https://auth.example.com',
      audience: 'https://api.example.com',
    });

    req.user = payload;
    next();
  } catch (error) {
    console.error('JWT validation failed:', error.message);
    res.status(401).json({ error: 'Invalid token' });
  }
}

module.exports = { validateJwt };
```

## Error Handling

```javascript
// src/routes/auth.js (add error route)
router.get('/error', (req, res) => {
  const message = req.query.message || 'An authentication error occurred';
  res.render('auth-error', { message });
});
```

## Related Files

- [Authorization Code Flow](../flows/authorization-code.md)
- [Security Best Practices](../security/best-practices.md)
