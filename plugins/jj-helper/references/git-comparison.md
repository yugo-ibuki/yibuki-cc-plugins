# Git vs jj コマンド比較

このドキュメントはGitユーザーがjjに移行する際のガイドです。

## Gitユーザーが最初に知るべきこと

### 1. ステージングエリアがない

```bash
# Git: ファイルを選んでステージング → コミット
git add file1.txt file2.txt
git commit -m "変更"

# jj: 編集したら即座に「現在のコミット」に反映される
vim file1.txt file2.txt
# この時点で既に現在のコミットに含まれている
jj describe -m "変更"  # メッセージを設定
jj new  # 次の作業用に新しいコミットを作成
```

**メリット**: `git add`忘れがない、部分コミットの心配不要
**注意点**: 一部のファイルだけコミットしたい場合は`jj split`を使う

### 2. 作業コピーは常にコミット

```bash
# Git: 作業中の変更はコミットされるまで「宙ぶらりん」
git status  # "Changes not staged for commit"

# jj: 作業コピー自体が「空のコミット」として存在
jj st  # 常にコミットの中にいる
jj log  # 作業中の変更も履歴に表示される（@ マークで表示）
```

**メリット**:
- `git stash`が不要（別の作業に移っても変更は消えない）
- 作業中でも履歴として追跡される
- 間違って`git reset --hard`で消す心配がない

### 3. 履歴は不変（Immutable）

```bash
# Git: rebaseやamendで履歴を「書き換える」
git commit --amend  # 直前のコミットを変更
git rebase -i HEAD~3  # 履歴を編集

# jj: 履歴は変更されず、新しい状態が作られる
jj squash  # 新しいコミットが作られる（古いのは隠れるだけ）
jj op log  # すべての操作履歴が残っている
jj undo  # いつでも元に戻せる
```

**メリット**:
- `git reflog`よりも強力なundo
- 間違った操作からの復旧が簡単
- `force push`しても怖くない

### 4. ブランチ名は必須ではない

```bash
# Git: ブランチを作ってから作業開始
git checkout -b feature-x

# jj: ブランチ名なしで作業可能
jj new main  # mainから分岐（名前なし）
# 作業...
jj bookmark create feature-x  # 後から名前をつける（push時に必要）
```

**メリット**:
- 実験的な作業がしやすい
- ブランチ名を考える必要がない
- 複数の作業を並行して進めやすい

## よくある質問: Gitではこうやってたけど？

### Q: 一部のファイルだけコミットしたい

```bash
# Git
git add specific_file.txt
git commit -m "一部だけ"

# jj: splitを使う
jj split specific_file.txt
# エディタが開き、分割するファイル/行を選択
```

### Q: 直前のコミットに追加の変更を含めたい

```bash
# Git
git add .
git commit --amend --no-edit

# jj: 方法1 - 現在の変更を親にsquash
jj squash

# jj: 方法2 - 親を直接編集
jj edit @-
# 編集...
jj new  # 戻る
```

### Q: コミットメッセージを変更したい

```bash
# Git
git commit --amend  # 直前
git rebase -i HEAD~3  # 古いコミット

# jj
jj describe -m "新しいメッセージ"  # 現在
jj describe @- -m "新しいメッセージ"  # 親
jj describe <revision> -m "新しいメッセージ"  # 任意のコミット
```

### Q: 特定のコミットを修正したい

```bash
# Git: インタラクティブリベースでedit
git rebase -i HEAD~5
# 該当コミットをeditに変更
# 修正...
git commit --amend
git rebase --continue

# jj: editで直接移動
jj edit <revision>
# 修正...（自動的にそのコミットに反映）
jj new  # 新しい作業に戻る
# リベースは自動的に行われる
```

### Q: コミットの順序を変えたい

```bash
# Git
git rebase -i HEAD~3
# エディタで行を並べ替え

# jj
jj rebase -r <移動するコミット> --before <移動先>
# または
jj rebase -r <移動するコミット> --after <移動先>
```

### Q: 間違った操作を取り消したい

```bash
# Git: reflogから探して復元
git reflog
git reset --hard HEAD@{2}

# jj: undoで即座に戻る
jj undo  # 直前の操作を取り消し
# または
jj op log  # 操作履歴を確認
jj op restore <operation-id>  # 特定の状態に復元
```

### Q: 作業中に急いで別のブランチを見たい

```bash
# Git: stashして移動
git stash
git checkout other-branch
# 確認...
git checkout -
git stash pop

# jj: そのまま移動（作業は保存されている）
jj new other-branch
# 確認...
jj new <元のchange-id>  # jj logで確認できる
```

### Q: マージコンフリクトが発生した

```bash
# Git
git merge feature
# コンフリクト発生
vim conflicted_file.txt
git add conflicted_file.txt
git commit

# jj
jj new main feature  # マージコミット作成
# コンフリクト発生
vim conflicted_file.txt
# マーカーを削除すると自動的に解決
jj st  # 解決を確認
```

**jjの特徴**: コンフリクト状態でもコミットを続けられる（後で解決可能）

### Q: PRのレビュー指摘に対応したい

```bash
# Git: 追加コミットか、fixupしてrebase
git commit -m "fix: レビュー対応"
# または
git commit --fixup <対象commit>
git rebase -i --autosquash

# jj: 該当コミットを直接編集
jj log  # 変更したいコミットを確認
jj edit <revision>
# 修正...
jj new  # 戻る
jj git push --bookmark <branch>  # 自動的にリベースされている
```

## jjの利点まとめ

| 観点 | Git | jj |
|------|-----|-----|
| 学習曲線 | 急（ステージング、HEAD、インデックス等） | 緩やか（シンプルな概念） |
| 取り消し | 複雑（reflog知識必要） | 簡単（`jj undo`） |
| 履歴編集 | インタラクティブリベース | 直接編集可能 |
| 並行作業 | stash必要 | 自然に可能 |
| コンフリクト | 解決するまでブロック | 後回しにできる |
| 実験的作業 | ブランチ名必須 | 匿名で可能 |
| 安全性 | 操作次第で危険 | 履歴不変で安全 |

## jjで注意すべき点

1. **push時はbookmark必要**: GitHubにpushするにはbookmarkが必要
2. **push後のtrack**: jj 0.37.0+ではpush後に`jj bookmark track <name>@origin`が必要（または`git.auto-local-bookmark`設定で自動化）
3. **IDEサポート**: Git統合ほど充実していない（colocatedで回避可能）
4. **チーム導入**: 全員がjjを使う必要はない（Git互換）
5. **GUIツール**: 少ない（CLIがメイン）

## 概念の違い

| Git | jj | 説明 |
|-----|-----|------|
| Staging area | なし | jjではステージングがなく、すべての変更が即座にコミットに反映 |
| Branch | Bookmark | jjのbookmarkはGitブランチと似ているが、匿名ブランチも可能 |
| HEAD | @ | 現在の作業コピーを指す |
| Stash | 不要 | 作業コピーが常にコミットなので、stash不要 |
| N/A | Operation log | すべての操作が記録され、undoが可能 |

## リポジトリ操作

| 操作 | Git | jj |
|------|-----|-----|
| 初期化 | `git init` | `jj git init` |
| 初期化（colocated） | - | `jj git init --colocate` |
| クローン | `git clone <url>` | `jj git clone <url>` |

## 状態確認

| 操作 | Git | jj |
|------|-----|-----|
| 状態確認 | `git status` | `jj st` / `jj status` |
| 差分（作業コピー） | `git diff` | `jj diff` |
| 差分（ステージ済み） | `git diff --staged` | N/A（ステージングなし） |
| 差分（コミット済み） | `git diff HEAD` | `jj diff` |
| 差分（特定リビジョン） | `git diff <rev>^ <rev>` | `jj diff -r <rev>` |
| ログ | `git log` | `jj log` |
| ログ（グラフ） | `git log --oneline --graph` | `jj log` |
| ログ（現在まで） | `git log` | `jj log -r ::@` |
| 特定コミットの詳細 | `git show <rev>` | `jj show <rev>` |
| blame | `git blame <file>` | `jj file annotate <file>` |

## コミット操作

| 操作 | Git | jj |
|------|-----|-----|
| ステージング | `git add <file>` | N/A（自動） |
| コミット | `git commit -m "msg"` | `jj commit -m "msg"` |
| 全てコミット | `git commit -a -m "msg"` | `jj commit -m "msg"` |
| 修正（amend） | `git commit --amend` | `jj squash` |
| メッセージ変更 | `git commit --amend --only` | `jj describe -m "msg"` |
| 親のメッセージ変更 | - | `jj describe @- -m "msg"` |

## ブランチ操作

| 操作 | Git | jj |
|------|-----|-----|
| 一覧表示 | `git branch` | `jj bookmark list` |
| 作成 | `git branch <name>` | `jj bookmark create <name>` |
| 作成+移動 | `git checkout -b <name>` | `jj new <base>` + `jj bookmark create <name>` |
| 削除 | `git branch -d <name>` | `jj bookmark delete <name>` |
| 移動 | `git branch -f <name> <rev>` | `jj bookmark set <name> -r <rev>` |
| 切り替え | `git checkout <name>` | `jj new <name>` / `jj edit <name>` |

## 変更操作

| 操作 | Git | jj |
|------|-----|-----|
| 新しい作業開始 | `git checkout -b <name> <base>` | `jj new <base>` |
| 特定コミットに移動 | `git checkout <rev>` | `jj new <rev>` / `jj edit <rev>` |
| 変更を取り消し | `git checkout -- <file>` | `jj restore <file>` |
| 全変更を取り消し | `git reset --hard` | `jj abandon` |
| コミットを破棄 | `git reset --hard HEAD^` | `jj abandon` |

## リベース・マージ

| 操作 | Git | jj |
|------|-----|-----|
| リベース | `git rebase <dest>` | `jj rebase -d <dest>` |
| インタラクティブリベース | `git rebase -i` | `jj rebase -r <revs> -d <dest>` |
| cherry-pick | `git cherry-pick <rev>` | `jj duplicate <rev>` |
| マージ | `git merge <branch>` | `jj new <current> <branch>` |

## Stash相当の操作

Gitの`git stash`はjjでは不要。作業コピーが常にコミットなので:

```bash
# Git
git stash
git checkout other-branch
# 作業...
git checkout original-branch
git stash pop

# jj
jj new other-branch  # 現在の作業は自動的に保存される
# 作業...
jj new <元のchange-id>  # 戻る
```

## リモート操作

| 操作 | Git | jj |
|------|-----|-----|
| フェッチ | `git fetch` | `jj git fetch` |
| プル | `git pull` | `jj git fetch` + `jj rebase -d <remote>` |
| プッシュ | `git push` | `jj git push --bookmark <name>` |
| 全てプッシュ | `git push --all` | `jj git push --all` |
| リモート追加 | `git remote add <name> <url>` | `jj git remote add <name> <url>` |

## Undo / Redo

| 操作 | Git | jj |
|------|-----|-----|
| 直前を取り消し | `git reset --hard HEAD^` | `jj undo` |
| reflog | `git reflog` | `jj op log` |
| 特定状態に復元 | `git reset --hard <ref>` | `jj op restore <op-id>` |

## 実用的な変換例

### Git: フィーチャーブランチで作業

```bash
# Git
git checkout -b feature main
# 編集...
git add .
git commit -m "feat: new feature"
git push origin feature
```

```bash
# jj
jj new main
# 編集...
jj describe -m "feat: new feature"
jj bookmark create feature
jj git push --bookmark feature
jj bookmark track feature@origin  # リモートとの追跡を設定
```

### Git: 直前のコミットを修正

```bash
# Git
# 編集...
git add .
git commit --amend
```

```bash
# jj
# 編集...（自動的に現在のコミットに反映）
# または親を修正したい場合:
jj squash
```

### Git: 作業中に別ブランチに移動

```bash
# Git
git stash
git checkout other-branch
# 作業...
git checkout -
git stash pop
```

```bash
# jj
jj new other-branch
# 作業...
jj new <元のchange-id>  # jj logで確認
```

### Git: cherry-pick

```bash
# Git
git cherry-pick abc123
```

```bash
# jj
jj duplicate abc123
```

### Git: インタラクティブリベース（順序変更）

```bash
# Git
git rebase -i HEAD~3
# エディタで順序変更
```

```bash
# jj
jj rebase -r <commit-to-move> --before <target>
# または --after
```

## 考え方のシフト: GitからjjへのMindset Change

### 1. 「ステージング」から「常にコミット」へ

**Git思考**: 「変更をレビューしてからコミットに含める」
```bash
git diff           # 変更を確認
git add -p         # 一部だけステージング
git commit         # コミット
```

**jj思考**: 「すべての変更は即座にコミットの一部。後で整理する」
```bash
# 編集するだけ（自動的にコミットに含まれる）
jj diff            # 変更を確認
jj split           # 必要なら後で分割
```

### 2. 「ブランチ中心」から「変更中心」へ

**Git思考**: 「まずブランチを作る → その上で作業」
```bash
git checkout -b feature/login
# 作業...
```

**jj思考**: 「まず変更を作る → 必要ならブランチ名をつける」
```bash
jj new main                    # 名前なしで作業開始
# 作業...
jj bookmark create feature/login  # push時に名前をつける
```

### 3. 「履歴書き換え」から「履歴追記」へ

**Git思考**: 「rebaseで履歴をきれいにする（危険な操作）」
```bash
git rebase -i HEAD~5   # 履歴を書き換える（元に戻すのが難しい）
```

**jj思考**: 「新しい状態を作る（古い状態は隠れるだけ）」
```bash
jj rebase ...          # 新しい状態が作られる
jj undo                # いつでも元に戻せる
jj op log              # すべての操作が記録されている
```

### 4. 「コミット完了まで不安定」から「常に安定」へ

**Git思考**: 「作業中の変更はどこにも保存されていない」
```bash
# 作業中に停電 → 変更が消える
# 急に別作業 → stashが必要
```

**jj思考**: 「作業中の変更も常にコミットとして存在」
```bash
# 作業中に停電 → 作業コピーのコミットとして残っている
# 急に別作業 → そのまま移動（元の作業は残っている）
```

### 5. 「HEAD」から「@」へ

**Git思考**: 「HEADはブランチの先端を指す」
```bash
git log HEAD          # 現在のブランチのログ
git reset HEAD~1      # HEADを1つ戻す
```

**jj思考**: 「@は現在の作業コピー（常にコミット）」
```bash
jj log -r @           # 現在の作業コピー
jj log -r @-          # 親コミット
jj log -r '@-3::@'    # 3つ前から現在まで
```

### マインドセットまとめ

| Git | jj | 考え方 |
|-----|-----|--------|
| コミットは「保存」 | コミットは「スナップショット」 | jjでは常に保存されている |
| ブランチは「作業場所」 | ブランチは「ラベル」 | jjではラベルなしでも作業可能 |
| 履歴は「編集可能」 | 履歴は「追記のみ」 | jjではすべての操作が記録される |
| stashは「一時保存」 | stash不要 | jjでは作業コピーもコミット |
| HEADは「現在位置」 | @は「現在の作業」 | jjでは作業自体がコミット |

### 移行のコツ

1. **最初はcolocatedで始める**: `jj git init --colocate`でGitと併用
2. **ステージングを忘れる**: 編集したらそのままでOK
3. **`jj undo`を信頼する**: 失敗しても必ず戻れる
4. **匿名ブランチを活用**: ブランチ名は後から考える
5. **`jj op log`を確認する習慣**: 操作履歴が見られると安心
6. **auto-local-bookmarkを設定する**: `jj config set --user git.auto-local-bookmark true` で push 後の track を自動化