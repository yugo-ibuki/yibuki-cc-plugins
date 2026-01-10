---
allowed-tools:
  - Read
  - Write
  - Bash(mkdir:*)
  - Bash(cp:*)
  - Bash(chmod:*)
  - Bash(npm:*)
  - Bash(pip:*)
description: 未使用import削除フックをセットアップ
argument-hint: [project-path]
model: claude-3-5-haiku-20241022
---

# 未使用Import削除フックセットアップ

コミット前に自動で未使用のimportを削除するフックをプロジェクトにセットアップします。

## 概要

このコマンドは、Claude Code の `PreToolCall` フックを使用して、`git commit` 実行前に変更ファイルから未使用のimportを自動削除します。

## 対応言語

| 言語 | 拡張子 | 使用ツール |
|------|--------|------------|
| TypeScript/JavaScript | `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs` | eslint + eslint-plugin-unused-imports または biome |
| Python | `.py` | ruff (推奨) または autoflake |
| Go | `.go` | goimports |

## セットアップ手順

### 1. スクリプトのコピー

プロジェクトの `.claude/hooks/` ディレクトリにスクリプトをコピーします。

```bash
mkdir -p .claude/hooks
cp <plugin-path>/scripts/remove-unused-imports.sh .claude/hooks/
chmod +x .claude/hooks/remove-unused-imports.sh
```

### 2. フック設定の追加

プロジェクトの `.claude/settings.json` に以下のフック設定を追加します。

```json
{
  "hooks": {
    "PreToolCall": [
      {
        "matcher": "Bash(git commit:*)",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/remove-unused-imports.sh"
          }
        ]
      }
    ]
  }
}
```

### 3. 言語別ツールのインストール

#### TypeScript/JavaScript プロジェクトの場合

**Option A: eslint-plugin-unused-imports (推奨)**

```bash
npm install -D eslint eslint-plugin-unused-imports @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

`.eslintrc.json` に追加:
```json
{
  "plugins": ["unused-imports", "@typescript-eslint"],
  "rules": {
    "unused-imports/no-unused-imports": "error"
  }
}
```

**Option B: Biome**

```bash
npm install -D @biomejs/biome
npx biome init
```

#### Python プロジェクトの場合

**Option A: ruff (推奨)**

```bash
pip install ruff
```

**Option B: autoflake**

```bash
pip install autoflake
```

#### Go プロジェクトの場合

```bash
go install golang.org/x/tools/cmd/goimports@latest
```

## 実行フロー

```
1. ユーザーが `git commit` を実行
2. Claude Code の PreToolCall フックが発火
3. remove-unused-imports.sh が実行される
4. ステージングされたファイルから未使用importを削除
5. 変更されたファイルを再ステージング
6. 本来の `git commit` が実行される
```

## ワークフロー

1. **現在のプロジェクト構成を確認**
   - `.claude/settings.json` の存在確認
   - `.claude/hooks/` ディレクトリの確認
   - プロジェクトで使用されている言語を検出

2. **スクリプトのセットアップ**
   - `.claude/hooks/` ディレクトリを作成
   - `remove-unused-imports.sh` をコピー

3. **設定ファイルの更新**
   - `.claude/settings.json` にフック設定を追加
   - 既存の設定がある場合はマージ

4. **ツールのインストール案内**
   - 検出された言語に応じて必要なツールをリストアップ
   - インストールコマンドを提示

## 注意事項

- フックはコミット対象のファイルのみを処理します
- ツールがインストールされていない言語のファイルは警告を出してスキップします
- 既存の eslint / biome / ruff 設定がある場合、それを優先して使用します
