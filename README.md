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

# APM 側の marketplace 定義を検証
apm pack --dry-run -v

# 生成結果を確認したい場合は、既存の Claude Code marketplace を直接上書きしない
apm pack --marketplace-output /tmp/yibuki-cc-plugins-marketplace.json
```

`apm.yml` は APM 用の marketplace authoring 定義です。既存の `.claude-plugin/marketplace.json` は Claude Code marketplace として手元の形式を維持します。`apm pack` は marketplace JSON を正規化して `author` などの既存メタデータを落とすことがあるため、通常は `--dry-run` または `--marketplace-output` で確認してください。

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
