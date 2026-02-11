---
name: jj-helper
description: Jujutsu (jj) version control helper. jjコマンドの使い方、ワークフロー、Gitとの比較、トラブルシューティングをサポート
---

# Jujutsu (jj) Helper Skill

Git互換の次世代バージョン管理システム「jj」の包括的なサポートを提供します。

## When to Use This Skill

このスキルは以下の場合に使用されます:
- jjコマンドの使い方を知りたいとき
- Gitコマンドに対応するjjコマンドを調べたいとき
- jjのワークフローやベストプラクティスを学びたいとき
- jj特有の機能（revsets、operation log等）を理解したいとき
- jjでのトラブルシューティング

## Gitユーザー向け: 考え方の違い

jjはGitと互換性がありますが、考え方が根本的に異なります。

| Git | jj | 何が変わる？ |
|-----|-----|-------------|
| ステージング→コミット | 編集=即コミット | `git add`不要、忘れる心配なし |
| コミットは「保存」 | 作業コピーも「コミット」 | stash不要、常に安全 |
| ブランチ必須 | 匿名ブランチOK | 実験が気軽、名前は後から |
| 履歴を「書き換え」 | 履歴は「追記」 | `jj undo`で何でも戻せる |
| `git reflog`で復旧 | `jj op log`で確認 | すべての操作が記録 |

**Gitユーザーへの一言**: 「add忘れた」「stashし忘れた」「rebase失敗した」がなくなります。

詳細は `references/git-comparison.md` を参照。

## Core Concepts

### Working Copy = Always a Commit

jjでは、作業コピーの状態は常にコミットです。Gitと異なり、ステージングエリアはありません。

```bash
# Git: 編集 → add → commit（3ステップ）
# jj:  編集（終わり。既にコミットの一部）

echo "hello" > file.txt
jj st  # 変更が即座に反映されている
jj describe -m "メッセージ"  # 後からメッセージを設定
jj new  # 次の作業用に新しいコミットを作成
```

### Immutable History

すべての操作は新しい状態を作成し、既存の履歴は変更されません。これにより安全なundo/redoが可能です。

```bash
# Git: git reset --hard で消えたら reflog から復旧（難しい）
# jj:  jj undo で即座に戻る（簡単）

jj op log  # 操作履歴を確認
jj undo    # 直前の操作を取り消し
jj op restore <id>  # 特定の状態に復元
```

### Bookmarks (≠ Git Branches)

jjの「bookmark」はGitのブランチに相当しますが、概念が異なります。jjでは匿名ブランチでも作業可能です。

```bash
# Git: まずブランチを作る
git checkout -b feature

# jj: まず作業、後でブランチ名
jj new main  # 名前なしで分岐
# 作業...
jj bookmark create feature  # push時に名前をつける
```

### Bookmark Tracking（重要: jj 0.37.0+）

jj 0.37.0以降、push後にリモートに作られたbookmarkを**自動でtrackしない**のがデフォルトの動作です。trackしないと、次回の`jj git fetch`時にリモートの変更がローカルbookmarkに反映されません。

```bash
# 毎回必要なフルワークフロー
jj bookmark create my-branch
jj git push --bookmark my-branch
jj bookmark track my-branch@origin  # ← これを忘れると diverged エラーの原因に

# 自動trackを有効にする設定（推奨）
jj config set --user git.auto-local-bookmark true
# これを設定すれば、push後に自動でtrackされるようになる
```

## Quick Reference

### 基本コマンド

| 操作 | コマンド | 説明 |
|------|---------|------|
| 初期化 | `jj git init` | 新規リポジトリ作成 |
| クローン | `jj git clone <url>` | リポジトリをクローン |
| 状態確認 | `jj st` | 現在の状態を表示 |
| 差分表示 | `jj diff` | 現在の変更を表示 |
| ログ表示 | `jj log` | コミット履歴を表示 |
| 説明追加 | `jj describe -m "msg"` | コミットメッセージを設定 |
| 新規変更 | `jj new` | 新しい空のコミットを作成 |
| コミット | `jj commit -m "msg"` | 変更を確定して新コミット作成 |

### Git比較表

| Git | jj | 備考 |
|-----|-----|------|
| `git init` | `jj git init` | colocatedオプションあり |
| `git clone` | `jj git clone` | |
| `git status` | `jj st` | |
| `git diff HEAD` | `jj diff` | |
| `git add && git commit` | `jj commit` | ステージング不要 |
| `git commit --amend` | `jj squash` | |
| `git log --graph` | `jj log` | |
| `git checkout -b` | `jj new main` | ブランチ名は後から |
| `git rebase` | `jj rebase` | より柔軟 |
| `git cherry-pick` | `jj duplicate` | |
| `git reset --hard` | `jj abandon` | |
| `git stash` | 不要 | 作業コピーが常にコミット |
| N/A | `jj op log` | 操作履歴 |
| N/A | `jj undo` | 操作の取り消し |

## Common Workflows

### 1. 基本的な作業フロー

```bash
# リポジトリをクローン
jj git clone https://github.com/user/repo.git
cd repo

# 現在の状態を確認
jj st
jj log

# ファイルを編集（自動的にコミットに反映）
vim src/main.rs

# 差分を確認
jj diff

# コミットメッセージを設定
jj describe -m "Fix: ユーザー認証のバグを修正"

# 次の作業用に新しいコミットを作成
jj new

# リモートにプッシュ（bookmarkが必要）
jj bookmark create my-feature
jj git push --bookmark my-feature
jj bookmark track my-feature@origin  # リモートとの追跡を設定
```

### 2. Squash Workflow（推奨）

小さな変更を積み重ねて、最後にまとめる方法:

```bash
# 作業開始
jj new main -m "WIP: 新機能の実装"

# 小さな変更を積み重ねる
vim file1.rs
jj new  # 次の変更へ

vim file2.rs
jj new  # 次の変更へ

# 変更をまとめる（親コミットにsquash）
jj squash

# 最終的なメッセージを設定
jj describe -m "feat: 新機能を実装"
```

### 3. Edit Workflow

既存のコミットを直接編集する方法:

```bash
# 編集したいコミットに移動
jj edit <revision>

# 変更を加える
vim file.rs

# 元の位置に戻る
jj new  # または jj edit @-
```

### 4. Conflict Resolution

```bash
# コンフリクトが発生した場合
jj st  # コンフリクトファイルを確認

# ファイルを編集してコンフリクトを解決
vim conflicted_file.rs

# コンフリクトマーカーを削除すると自動的に解決される
jj st  # コンフリクトが解消されたことを確認
```

## Revsets

リビジョンを指定するための強力なクエリ言語:

| Revset | 意味 |
|--------|------|
| `@` | 現在の作業コピー |
| `@-` | 現在の親コミット |
| `root()` | ルートコミット |
| `heads()` | すべてのhead |
| `trunk()` | メインブランチ |
| `visible_heads()` | 可視のhead |
| `xyz` | 変更ID（短縮可） |
| `xyz::` | xyzとその子孫 |
| `::xyz` | xyzとその祖先 |
| `x & y` | AND |
| `x \| y` | OR |
| `~x` | NOT |

### Revset例

```bash
# 現在の変更とその祖先を表示
jj log -r '::@'

# mainから分岐したすべての変更
jj log -r 'trunk()..@'

# 最近の10コミット
jj log -r '@-10::@'

# 特定のファイルを変更したコミット
jj log -r 'file("src/main.rs")'
```

## Git Interop

### Colocated Repository

jjとGitを同じディレクトリで併用:

```bash
# colocatedリポジトリとして初期化
jj git init --colocate

# または既存のGitリポジトリでjjを使用
cd existing-git-repo
jj git init --colocate
```

### リモート操作

```bash
# フェッチ
jj git fetch

# プッシュ
jj git push --bookmark <bookmark-name>

# すべてのbookmarkをプッシュ
jj git push --all
```

## Troubleshooting

### よくある問題

**Q: 間違った操作をしてしまった**
```bash
jj op log  # 操作履歴を確認
jj undo    # 直前の操作を取り消し
# または
jj op restore <operation-id>  # 特定の状態に復元
```

**Q: コミットを破棄したい**
```bash
jj abandon <revision>
```

**Q: 変更を別のコミットに移動したい**
```bash
jj squash --from <source> --into <destination>
```

**Q: bookmarkを作成し忘れてpushできない**
```bash
jj bookmark create <name> -r @
jj git push --bookmark <name>
jj bookmark track <name>@origin  # 追跡を設定
```

**Q: Gitブランチと同期したい**
```bash
jj git fetch
jj bookmark track <branch>@origin
```

**Q: push後にbookmarkが「diverged」になる**
```bash
# 原因: push後にtrackしていなかった
jj bookmark track <name>@origin

# 今後の予防: 自動trackを有効にする
jj config set --user git.auto-local-bookmark true
```

## Documentation Reference

詳細は以下のドキュメントを参照:

- `references/commands.md` - 全コマンドリファレンス
- `references/workflows.md` - 詳細なワークフロー説明
- `references/git-comparison.md` - Git比較の詳細

## External Resources

### Official

- [Official Documentation](https://docs.jj-vcs.dev/latest/)
- [CLI Reference](https://www.jj-vcs.dev/latest/cli-reference/)
- [GitHub Repository](https://github.com/jj-vcs/jj)
- [Steve's Jujutsu Tutorial](https://steveklabnik.github.io/jujutsu-tutorial/)

### Japanese Articles (Zenn)

- [jjの使い方](https://zenn.dev/wartemeinnicht/articles/3059bcf2cd186d) - 基本的な使い方ガイド
- [jjを使ってみた](https://zenn.dev/k_ing/articles/c7ab23fda46a12) - 入門記事
- [jj: Gerrit哲学](https://zenn.dev/imudak/articles/jj-gerrit-philosophy) - Gerritとの関連性
- [jj: 並行作業](https://zenn.dev/imudak/articles/jj-parallel-work) - 並行作業のワークフロー
- [jj: Rebase vs Merge](https://zenn.dev/imudak/articles/jj-rebase-vs-merge) - RebaseとMergeの比較
- [jj入門](https://zenn.dev/kimkiyong/articles/1806beccb74a88) - 入門ガイド
- [jj: モダンVCSガイド](https://zenn.dev/yamitake/articles/jj-jujutsu-modern-vcs-guide) - 包括的なガイド

---

Generated for Jujutsu (jj) version control system