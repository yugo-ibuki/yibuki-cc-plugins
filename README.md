# プロジェクト名

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