# プロジェクト名

## APM

このリポジトリは [APM (Agent Package Manager)](https://github.com/microsoft/apm) の marketplace authoring に対応しています。

### セットアップ

```bash
# APM CLI が未インストールの場合
brew install microsoft/apm/apm

# marketplace authoring は v0.11.0 以降を推奨
apm --version
apm update

# marketplace 定義を検証
apm pack --dry-run -v

# apm.yml から .claude-plugin/marketplace.json を再生成
apm pack
```

`apm.yml` を編集元、`.claude-plugin/marketplace.json` を生成物として扱います。プラグインを追加・更新したら `apm.yml` の `marketplace.packages` を更新し、`apm pack` を実行して両方のファイルをコミットしてください。

`apm marketplace check` は remote source の ref 解決確認向けです。このリポジトリのように `source: ./plugins/...` のローカルパス package を使う場合は、`apm pack --dry-run -v` で生成確認してください。

## 新しいプラグインの追加

### プラグイン追加手順

1. プラグインディレクトリを作成:

```bash
mkdir -p ./plugins/commands/your-plugin-name
```

2. プラグインファイルを作成:

```bash
touch ./plugins/commands/your-plugin-name/your-plugin-name.md
```

3. manifest.jsonに追加:

```json
{
  "name": "your-plugin-name",
  "source": "./plugins/commands/your-plugin-name",
  "description": "プラグインの説明",
  "version": "1.0.0",
  "author": {
    "name": "あなたの名前"
  }
}
```

4. プラグインをテスト:

```bash
# テストコマンド
```

## 貢献

貢献のガイドラインをここに記載。

## ライセンス

ライセンス情報をここに記載。
