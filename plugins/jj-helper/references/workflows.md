# jj ワークフローガイド

## 1. Squash Workflow（推奨）

最も一般的で推奨されるワークフロー。小さな変更を積み重ねて、最後にまとめる方法。

### 基本の流れ

```bash
# 1. 作業を開始（mainから分岐）
jj new main -m "WIP: 新機能の実装"

# 2. ファイルを編集
vim src/feature.rs

# 3. 次の変更のために新しいコミットを作成
jj new -m "WIP: テスト追加"

# 4. さらに編集
vim tests/feature_test.rs

# 5. 変更を確認
jj log -r 'trunk()..@'

# 6. 変更を親にsquash（まとめる）
jj squash

# 7. 最終的なメッセージを設定
jj describe -m "feat: ユーザー認証機能を実装"

# 8. bookmarkを作成してpush
jj bookmark create auth-feature
jj git push --bookmark auth-feature
jj bookmark track auth-feature@origin  # リモートとの追跡を設定
```

### メリット
- 作業中は自由にコミット
- 最終的にきれいな履歴
- いつでも途中状態に戻れる

## 2. Edit Workflow

既存のコミットを直接編集する方法。PRのレビュー対応などに便利。

### 基本の流れ

```bash
# 1. 現在の状態を確認
jj log

# 2. 編集したいコミットに移動
jj edit <change-id>

# 3. 変更を加える
vim src/file.rs

# 4. 変更が自動的にそのコミットに反映される
jj st

# 5. 元の位置（最新）に戻る
jj new
```

### PRレビュー対応の例

```bash
# レビューで指摘された箇所を修正
jj log -r 'my-feature..'  # 変更を確認
jj edit <修正が必要なコミット>
vim src/file.rs  # 修正
jj new  # 新しいコミットへ
jj git push --bookmark my-feature
```

## 3. Anonymous Branch Workflow

bookmark（ブランチ名）なしで作業する方法。実験的な作業に便利。

```bash
# ブランチ名なしで作業開始
jj new main

# 複数の実験的ブランチを作成
jj new main -m "実験A"
# 作業...
jj new main -m "実験B"
# 作業...

# 良かった方を採用
jj log -r 'trunk()..visible_heads()'
jj bookmark create my-feature -r <採用するchange-id>
```

## 4. Stacked PRs（連続したPR）

依存関係のある複数のPRを管理。

```bash
# ベースの変更を作成
jj new main -m "feat: 基盤機能"
jj bookmark create base-feature
# 作業...

# 依存する変更を作成
jj new -m "feat: 基盤を使った機能A"
jj bookmark create feature-a
# 作業...

# さらに依存する変更
jj new -m "feat: 機能Aを拡張"
jj bookmark create feature-b

# すべてをpush
jj git push --all

# ベースが変更された場合
jj edit base-feature
# 修正...
jj new  # 子コミットは自動的にrebaseされる
```

## 5. コンフリクト解決

### 基本的な解決

```bash
# コンフリクトが発生
jj rebase -d main

# 状態を確認
jj st
# Conflicted files:
#   src/file.rs

# ファイルを編集してコンフリクトを解決
vim src/file.rs
# <<<<<<< と >>>>>>> のマーカーを削除して正しい内容にする

# 解決を確認
jj st  # コンフリクトが消えている
```

### コンフリクト状態のまま作業

jjではコンフリクト状態でもコミットを続けることができる:

```bash
# コンフリクトがあっても新しいコミットを作成可能
jj new

# 後で解決
jj edit <コンフリクトのあるコミット>
# 解決...
```

## 6. マージ操作

```bash
# 2つのブランチをマージ
jj new <branch-a> <branch-b> -m "merge: AとBを統合"

# trunk（main）にマージ
jj new trunk() <feature-branch>
jj describe -m "merge: 機能をmainにマージ"
```

## 7. 作業の取り消しとリカバリ

### 直前の操作を取り消し

```bash
jj undo
```

### 操作履歴から復元

```bash
# 操作履歴を確認
jj op log

# 特定の状態に復元
jj op restore <operation-id>
```

### コミットを破棄

```bash
# 単一のコミット
jj abandon <change-id>

# 範囲を破棄
jj abandon -r '<revision-set>'
```

### 変更を元に戻す

```bash
# ファイルを親の状態に戻す
jj restore <path>

# 特定のリビジョンから復元
jj restore --from <revision> <path>
```

## 8. Git Colocated Workflow

jjとGitを同じリポジトリで併用。

```bash
# 既存のGitリポジトリでjjを使用開始
cd my-git-repo
jj git init --colocate

# jjで作業
jj new main
# 編集...
jj describe -m "新機能"

# Gitコマンドも使用可能
git status
git log

# jjの状態をGitに同期
jj git export
```

## 9. GitHub PR Workflow

```bash
# 1. フェッチして最新を取得
jj git fetch

# 2. mainから新しい作業を開始
jj new main -m "feat: 新機能"

# 3. 開発作業
vim src/feature.rs

# 4. bookmarkを作成
jj bookmark create my-feature

# 5. プッシュ
jj git push --bookmark my-feature

# 6. リモートとの追跡を設定（jj 0.37.0+では必須）
jj bookmark track my-feature@origin

# 7. GitHub上でPRを作成

# 8. レビュー対応
jj git fetch  # レビューコメントを確認後
jj edit my-feature
# 修正...
jj new
jj git push --bookmark my-feature

# 9. マージ後のクリーンアップ
jj git fetch
jj bookmark delete my-feature
```

> **💡 Tips**: `jj config set --user git.auto-local-bookmark true` を設定すると、
> push後に自動でtrackされるようになり、手順6が不要になります。

## 10. Daily Workflow Example

```bash
# 朝: 最新を取得
jj git fetch

# 作業開始
jj new main -m "WIP: 今日のタスク"

# 作業中: 頻繁に状態確認
jj st
jj diff
jj log -r 'trunk()..@'

# 区切りの良いところでコミット
jj new -m "WIP: 続き"

# 作業完了: squashして整理
jj squash
jj describe -m "feat: 完成した機能"

# プッシュ
jj bookmark create todays-work
jj git push --bookmark todays-work
jj bookmark track todays-work@origin  # リモートとの追跡を設定
```