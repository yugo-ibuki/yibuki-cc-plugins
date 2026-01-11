---
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(find:*)
  - Bash(wc:*)
  - Task
description: タスクを並列実行可能なサブタスクに分割
argument-hint: <タスクの説明> [--fine|--coarse] [--with-files]
---

# /split-task コマンド

タスクを分析して並列実行可能なサブタスクに分割し、各サブタスクに関連ファイルを紐付けます。

## 参照スキル

- `skills/task-splitter/SKILL.md` - タスク分割ロジック

## 使用方法

```bash
# 基本的な使用
/split-task ログイン機能にOAuth対応を追加。Google/GitHubに対応。

# 粒度オプション
/split-task --fine ユーザー管理機能のリファクタリング    # 細かく分割
/split-task --coarse 決済システムの実装                  # 大まかに分割

# 関連ファイルを事前検索して渡す
/split-task --with-files 認証フローの改善
```

## オプション

| オプション | 説明 |
|-----------|------|
| `--fine` | 細かく分割（1サブタスク = 1ファイル程度） |
| `--coarse` | 大まかに分割（1サブタスク = 機能単位） |
| `--with-files` | 事前に関連ファイルを検索してから分割 |

## 実行フロー

### Step 1: タスク内容の解析

ユーザー入力からタスクの種別と範囲を特定:

- **新機能追加**: 新しい機能の実装
- **機能改善**: 既存機能の拡張や修正
- **リファクタリング**: コード品質の改善
- **バグ修正**: 不具合の修正
- **テスト追加**: テストカバレッジの向上

### Step 2: 関連ファイルの収集

`--with-files` オプション指定時、または関連ファイルが不明な場合:

```bash
# タスクのキーワードからファイルを検索
find . -type f \( -name "*keyword*" \) \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' 2>/dev/null

# 内容からファイルを検索
grep -rl "keyword" --include="*.ts" --include="*.tsx" \
  --include="*.js" --include="*.jsx" \
  --include="*.py" --include="*.go" . 2>/dev/null | head -30
```

または `project-onboarding` プラグインの `/find-files` コマンドを使用。

### Step 3: サブタスク分解

SKILL.md の分解ロジックに従ってタスクを分割:

1. **機能単位の特定**: 独立して実装可能な単位に分解
2. **依存関係の分析**: サブタスク間の依存を特定
3. **ファイル紐付け**: 各サブタスクに関連ファイルを割り当て
4. **フェーズ構成**: 並列実行可能なグループに整理

### Step 4: 出力生成

以下の形式で結果を出力:

```markdown
# タスク分割結果

## 元タスク
{original_task}

## サブタスク一覧

### Phase 1（並列実行可能）

| ID | タスク | 関連ファイル | 見積もり |
|----|--------|-------------|---------|
| 1-1 | OAuth基盤の実装 | `src/auth/oauth.ts`(新規) | 中 |
| 1-2 | Google OAuth実装 | `src/auth/providers/google.ts`(新規) | 小 |

### Phase 2（Phase 1完了後）

| ID | タスク | 関連ファイル | 依存 |
|----|--------|-------------|------|
| 2-1 | useAuth hook拡張 | `src/hooks/useAuth.ts` | 1-1 |

## 依存関係図

```
Phase 1 (並列)          Phase 2 (並列)
┌─────────────┐
│ 1-1 OAuth基盤│──────→ 2-1 useAuth拡張
└─────────────┘
┌─────────────┐
│ 1-2 Google   │
└─────────────┘
```

## 実行計画

```bash
# Phase 1: 並列実行
Task(1-1), Task(1-2) → 並列

# Phase 2: Phase 1完了後
Task(2-1) → 実行
```
```

## project-onboarding との連携

### 連携パターン1: 順次実行

```bash
# 1. 関連ファイルを検索
/find-files OAuth認証

# 2. 検索結果を参照してタスク分割
/split-task ログイン機能にOAuth対応を追加
```

### 連携パターン2: 自動連携

```bash
# --with-files オプションで自動的に関連ファイルを検索
/split-task --with-files ログイン機能にOAuth対応を追加
```

## 分割結果の活用

分割結果は以下のように活用できます:

### 並列実行

```python
# Phase 1のタスクを並列実行
Task(prompt="1-1: OAuth基盤の実装", files=["src/auth/oauth.ts"])  # 並列
Task(prompt="1-2: Google OAuth実装", files=["src/auth/providers/google.ts"])  # 並列

# Phase 2はPhase 1完了後
TaskOutput(task_id=phase1_tasks)  # 待機
Task(prompt="2-1: useAuth hook拡張", files=["src/hooks/useAuth.ts"])
```

### 進捗管理

分割結果をTodoWriteに変換して進捗を追跡:

```bash
# 各サブタスクをTodoとして登録
TodoWrite([
  {"content": "1-1: OAuth基盤の実装", "status": "pending"},
  {"content": "1-2: Google OAuth実装", "status": "pending"},
  {"content": "2-1: useAuth hook拡張", "status": "pending"},
])
```

## 見積もり基準

| 見積もり | ファイル数 | 複雑度 | 例 |
|---------|-----------|--------|-----|
| 小 | 1 | 明確なパターン | 型定義追加、設定変更 |
| 中 | 2-3 | ある程度の判断 | 新規コンポーネント、API追加 |
| 大 | 4+ | 設計判断が必要 | 新機能の基盤実装 |

## 注意事項

- サブタスクは最大20個まで
- フェーズは最大5段階まで
- 1サブタスクの関連ファイルは最大5個まで
- 循環依存が検出された場合はエラーを出力
