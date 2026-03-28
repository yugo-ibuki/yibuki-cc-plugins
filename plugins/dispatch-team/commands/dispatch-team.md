---
allowed-tools:
  - Read
  - Glob
  - Grep
  - Agent
  - Bash(find:*)
description: タスクに合わせてエージェントチームを編成し並列実行
argument-hint: <タスクの説明>
---

# /dispatch-team コマンド

タスクを分析して独立したサブタスクを特定し、それぞれに適切なエージェントを割り当てて並列実行する。

## 参照スキル

- `skills/dispatch-team/SKILL.md` - 並列エージェント編成ロジック

## 実行フロー

### Step 1: タスクの分析

`$ARGUMENTS` からタスク内容を取得し、独立したサブタスクに分解する。

### Step 2: 独立性の判定

各サブタスク間の依存関係を分析:
- 共有状態がないか
- 同じファイルを編集しないか
- 順序依存がないか

### Step 3: エージェント編成

各サブタスクに対して適切なAgentを割り当て:

| タスク種別 | 推奨Agent |
|-----------|-----------|
| コード探索・調査 | Explore |
| 設計・アーキテクチャ | Plan |
| バグ修正・実装 | general-purpose |
| コードレビュー | code-reviewer |
| テスト分析 | quality-engineer |
| セキュリティ確認 | security-engineer |

### Step 4: 並列実行

独立したサブタスクをAgent toolで同時にディスパッチ:

```
Agent(prompt="サブタスク1の内容", subagent_type="適切なtype")
Agent(prompt="サブタスク2の内容", subagent_type="適切なtype")
Agent(prompt="サブタスク3の内容", subagent_type="適切なtype")
```

### Step 5: 結果の統合

全エージェントの結果を収集し:
1. 各エージェントの成果をサマリー表示
2. 競合がないか確認
3. 統合結果をユーザーに提示
