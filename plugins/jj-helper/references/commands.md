# jj コマンドリファレンス

## リポジトリ管理

### jj git init
新しいjjリポジトリを初期化

```bash
# 標準初期化
jj git init

# Gitと併用（colocated）
jj git init --colocate

# 指定ディレクトリに作成
jj git init <path>
```

### jj git clone
リモートリポジトリをクローン

```bash
jj git clone <url> [<destination>]

# 例
jj git clone https://github.com/user/repo.git
jj git clone git@github.com:user/repo.git my-repo
```

## 状態確認

### jj status (jj st)
現在の作業コピーの状態を表示

```bash
jj st
jj status
```

### jj log
コミット履歴を表示

```bash
# 基本表示
jj log

# 特定のリビジョン範囲
jj log -r '::@'
jj log -r 'trunk()..@'

# 詳細表示
jj log --stat
jj log -p  # パッチ付き

# 1行表示
jj log --no-graph -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
```

### jj diff
変更差分を表示

```bash
# 現在の作業コピーの差分
jj diff

# 特定リビジョンの差分
jj diff -r <revision>

# ファイル指定
jj diff <path>

# 統計情報のみ
jj diff --stat
```

### jj show
特定のリビジョンの詳細を表示

```bash
jj show <revision>
jj show @-  # 親コミット
```

## 変更操作

### jj new
新しい空のコミットを作成

```bash
# 現在のコミットの子として
jj new

# 特定の親から
jj new <parent>
jj new main

# 複数の親（マージコミット）
jj new <parent1> <parent2>

# メッセージ付き
jj new -m "WIP: 新機能"
```

### jj describe
コミットメッセージを設定/変更

```bash
# 現在のコミット
jj describe -m "コミットメッセージ"

# エディタで編集
jj describe

# 特定のリビジョン
jj describe -r <revision> -m "メッセージ"

# 親コミット
jj describe @- -m "メッセージ"
```

### jj commit
現在の変更を確定して新しいコミットを作成

```bash
jj commit -m "メッセージ"

# エディタでメッセージ入力
jj commit
```

### jj edit
特定のコミットを作業コピーとして編集

```bash
jj edit <revision>

# 例: 親コミットを編集
jj edit @-
```

### jj squash
変更を親コミットにマージ

```bash
# 現在の変更を親にsquash
jj squash

# 特定のリビジョン間
jj squash --from <source> --into <destination>

# 一部のファイルのみ
jj squash <paths>
```

### jj split
コミットを複数に分割

```bash
# インタラクティブに分割
jj split

# ファイル指定
jj split <paths>
```

### jj abandon
コミットを破棄

```bash
jj abandon <revision>
jj abandon @  # 現在のコミット
```

### jj restore
ファイルを特定の状態に復元

```bash
# 親の状態に復元
jj restore <paths>

# 特定リビジョンから復元
jj restore --from <revision> <paths>
```

## Bookmark（ブランチ）操作

### jj bookmark create
新しいbookmarkを作成

```bash
jj bookmark create <name>
jj bookmark create <name> -r <revision>
```

### jj bookmark list
bookmarkの一覧表示

```bash
jj bookmark list
jj bookmark list --all  # リモート含む
```

### jj bookmark set
bookmarkを移動

```bash
jj bookmark set <name> -r <revision>
```

### jj bookmark delete
bookmarkを削除

```bash
jj bookmark delete <name>
```

### jj bookmark track
リモートbookmarkを追跡（jj 0.37.0+ではpush後に必須）

```bash
jj bookmark track <name>@<remote>

# 例: push後にリモートと追跡を設定
jj bookmark create my-branch
jj git push --bookmark my-branch
jj bookmark track my-branch@origin  # これを忘れるとdivergedエラーの原因に
```

## Rebase操作

### jj rebase
コミットを別の場所に移動

```bash
# 現在のコミットを移動
jj rebase -d <destination>

# 特定のブランチを移動
jj rebase -b <branch> -d <destination>

# ソースを指定
jj rebase -s <source> -d <destination>

# リビジョン範囲
jj rebase -r <revisions> -d <destination>
```

## Git連携

### jj git fetch
リモートから取得

```bash
jj git fetch
jj git fetch --remote <remote>
jj git fetch --all-remotes
```

### jj git push
リモートにプッシュ

```bash
# 特定のbookmark
jj git push --bookmark <name>

# すべてのbookmark
jj git push --all

# 変更セット
jj git push --change <revision>
```

### jj git remote
リモート管理

```bash
jj git remote list
jj git remote add <name> <url>
jj git remote remove <name>
```

## 操作履歴

### jj op log (jj operation log)
操作履歴を表示

```bash
jj op log
jj operation log
```

### jj undo
直前の操作を取り消し

```bash
jj undo
```

### jj op restore
特定の操作状態に復元

```bash
jj op restore <operation-id>
```

## その他

### jj duplicate
コミットを複製

```bash
jj duplicate <revision>
jj duplicate <revision> -d <destination>
```

### jj file annotate
ファイルの各行の最終変更を表示（git blameと同等）

```bash
jj file annotate <path>
```

### jj workspace
ワークスペース管理

```bash
jj workspace list
jj workspace add <path>
jj workspace forget <name>
```

### jj config
設定の表示/変更

```bash
jj config list
jj config set --user user.name "Your Name"
jj config set --user user.email "your@email.com"

# push後にbookmarkを自動でtrackする設定（推奨）
jj config set --user git.auto-local-bookmark true

# fetch時にリモートのbookmarkを自動trackする設定
jj config set --user remotes.origin.auto-track-bookmarks '*'
# '*' = すべてのbookmark、特定パターンも可（例: 'main' や 'release/*'）
```

**設定の違い**:
| 設定 | 効果 | タイミング |
|------|------|-----------|
| `git.auto-local-bookmark` | ローカルbookmarkをリモートに自動関連付け | push時 |
| `remotes.origin.auto-track-bookmarks` | リモートのbookmarkをローカルに自動track | fetch時 |