---
name: analyze-imports
description: ファイルのimport/export関係を解析し、依存ツリーと逆参照（どこから呼ばれているか）を特定する。monorepo構成でのパッケージ間依存も検出する。関連ファイル検索時に自動的に呼び出される。
version: "1.0.0"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(find:*)
  - Bash(cat:*)
---

# analyze-imports スキル

ファイルのimport/export関係を解析し、依存関係と呼び出し元を特定します。
monorepo構成にも対応し、パッケージ間の依存関係を可視化します。

## 機能概要

1. **順方向解析（Dependencies）**: ファイルがimportしているモジュールを取得
2. **逆方向解析（Dependents）**: そのファイルをimportしているファイルを検索
3. **monorepo解析**: どのパッケージ/アプリから参照されているかを整理

## monorepo検出

### パッケージマネージャー設定の検索

```bash
# monorepo の検出
find . -maxdepth 3 \( \
  -name "pnpm-workspace.yaml" -o \
  -name "lerna.json" -o \
  -name "nx.json" -o \
  -name "turbo.json" -o \
  -name "rush.json" \
\) 2>/dev/null

# packages/apps ディレクトリの検出
ls -d packages/* apps/* 2>/dev/null
```

### ワークスペース構成の解析

```yaml
# pnpm-workspace.yaml の例
packages:
  - 'packages/*'
  - 'apps/*'
```

```json
// turbo.json の例
{
  "pipeline": {
    "build": { "dependsOn": ["^build"] }
  }
}
```

## 順方向解析（Dependencies）

対象ファイルがimportしているモジュールを抽出:

### TypeScript/JavaScript

```bash
# import 文の抽出
grep -E "^import .+ from ['\"]" <file>
grep -E "require\(['\"]" <file>
grep -E "import\(['\"]" <file>  # dynamic import
```

**解析対象パターン:**
```typescript
import { foo } from './utils'           // 相対パス
import { bar } from '@myorg/shared'     // monorepoパッケージ
import axios from 'axios'                // 外部パッケージ
const mod = require('./module')          // CommonJS
const lazy = await import('./lazy')      // Dynamic import
```

### Python

```bash
grep -E "^from .+ import|^import " <file>
```

### Go

```bash
grep -E "^import \(|^\t\"" <file>
```

## 逆方向解析（Dependents）

対象ファイルをimportしているファイルを検索:

```bash
# ファイル名からモジュール名を抽出
# 例: src/utils/helper.ts → "utils/helper", "./helper", "@pkg/utils"

# 相対パスでの参照を検索
grep -rl "from ['\"].*helper['\"]" --include="*.ts" --include="*.tsx" .

# パッケージ名での参照を検索（monorepo）
grep -rl "from ['\"]@myorg/utils['\"]" --include="*.ts" .
```

## 出力フォーマット

```markdown
# Import解析: `src/services/authService.ts`

## このファイルがimportしているもの（Dependencies）

### 内部モジュール
| パス | エクスポート | 種別 |
|------|-------------|------|
| `./api/client` | { apiClient } | 相対パス |
| `../utils/validation` | { validateEmail } | 相対パス |
| `@myorg/shared` | { User, Token } | monorepoパッケージ |

### 外部パッケージ
| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| axios | ^1.6.0 | HTTP通信 |
| jsonwebtoken | ^9.0.0 | JWT処理 |

## このファイルを使用しているもの（Dependents）

### 同一パッケージ内
| ファイル | import形式 |
|---------|-----------|
| `src/pages/LoginPage.tsx` | `import { login } from '../services/authService'` |
| `src/hooks/useAuth.ts` | `import * as authService from '../services/authService'` |

### 他パッケージから（monorepo）
| パッケージ | ファイル | 用途 |
|-----------|---------|------|
| `apps/web` | `src/auth/index.ts` | Webアプリの認証 |
| `apps/mobile` | `src/services/auth.ts` | モバイルアプリの認証 |
| `packages/admin` | `src/lib/auth.ts` | 管理画面の認証 |

## 依存関係ツリー

```
authService.ts
├── imports:
│   ├── ./api/client.ts
│   │   └── axios (external)
│   ├── ../utils/validation.ts
│   └── @myorg/shared/types
│       └── packages/shared/src/types/index.ts
│
└── imported by:
    ├── [apps/web]
    │   ├── src/pages/LoginPage.tsx
    │   └── src/hooks/useAuth.ts
    ├── [apps/mobile]
    │   └── src/services/auth.ts
    └── [packages/admin]
        └── src/lib/auth.ts
```

## monorepo パッケージマップ

| パッケージ名 | パス | このファイルとの関係 |
|-------------|------|---------------------|
| @myorg/web | apps/web | 使用（3箇所） |
| @myorg/mobile | apps/mobile | 使用（1箇所） |
| @myorg/shared | packages/shared | 依存先 |
| @myorg/admin | packages/admin | 使用（1箇所） |

## 影響範囲の要約

- **直接影響**: 5ファイル
- **間接影響**（依存の依存）: 12ファイル
- **影響パッケージ**: 3パッケージ
- **変更時の注意**: `@myorg/web` と `@myorg/mobile` の両方でテストが必要
```

## 言語別のimport解析パターン

### TypeScript/JavaScript
```regex
# ESM import
^import\s+(?:\{[^}]+\}|\*\s+as\s+\w+|\w+)\s+from\s+['"]([^'"]+)['"]

# CommonJS require
(?:const|let|var)\s+\{?[\w\s,]+\}?\s*=\s*require\(['"]([^'"]+)['"]\)

# Dynamic import
import\(['"]([^'"]+)['"]\)

# Re-export
export\s+(?:\{[^}]+\}|\*)\s+from\s+['"]([^'"]+)['"]
```

### Python
```regex
^from\s+([\w.]+)\s+import
^import\s+([\w.]+)
```

### Go
```regex
^\s*"([^"]+)"
```

### Rust
```regex
^use\s+([\w:]+)
^mod\s+(\w+)
```

## 注意事項

- 循環参照を検出した場合は警告を表示
- node_modules, vendor, dist などは検索対象外
- 動的importやconditional requireは完全には追跡できない場合あり
- TypeScriptのpath aliasは tsconfig.json を参照して解決
