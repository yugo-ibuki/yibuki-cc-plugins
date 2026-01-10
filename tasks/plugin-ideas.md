# ローカルプラグインのアイデア集

Claude Codeでローカル開発をより効率化するためのプラグイン案。

---

## 1. code-review - コードレビュープラグイン

### 概要
変更したコードに対して自己レビューを実施し、レビューコメントをMarkdown形式で出力。

### ユースケース
- PR作成前のセルフレビュー
- コーディング規約違反の検出
- セキュリティリスクのチェック

### コマンド
```
/code-review [--security] [--performance] [--style]
```

### 機能
- `git diff` からの変更検出
- OWASP Top 10に基づくセキュリティチェック
- パフォーマンス懸念点の指摘
- 命名規則・コードスタイルの確認
- レビューレポートの生成 (`.claude/reviews/YYYY-MM-DD-review.md`)

---

## 2. refactor-suggest - リファクタリング提案プラグイン

### 概要
指定したファイルやディレクトリを分析し、リファクタリングの提案を行う。

### ユースケース
- 技術的負債の可視化
- コード品質改善計画の作成
- レガシーコードの改善指針

### コマンド
```
/refactor-suggest <path> [--depth=shallow|deep] [--focus=duplication|complexity|coupling]
```

### 機能
- 循環的複雑度の計算
- 重複コードの検出
- 依存関係の分析
- 改善優先度の提案
- リファクタリング計画の出力

---

## 3. test-gen - テスト生成プラグイン

### 概要
指定した関数やモジュールに対するテストコードを自動生成。

### ユースケース
- 新規機能のテスト作成
- カバレッジ向上
- TDD支援

### コマンド
```
/test-gen <file-or-function> [--framework=jest|vitest|pytest|go] [--coverage=basic|comprehensive]
```

### 機能
- 関数シグネチャからテストケース生成
- エッジケース・境界値テストの提案
- モックの自動生成
- 既存テストとの整合性確認

---

## 4. debug-helper - デバッグ支援プラグイン

### 概要
エラーメッセージやスタックトレースを解析し、原因と解決策を提案。

### ユースケース
- 複雑なエラーの原因特定
- スタックトレースの解読
- 類似問題の検索

### コマンド
```
/debug-helper [エラーメッセージ or ファイルパス]
```

### 機能
- スタックトレースの解析
- 関連するソースコードの特定
- 類似エラーパターンの提示
- 修正案の提案
- デバッグ手順のガイド

---

## 5. dependency-check - 依存関係チェックプラグイン

### 概要
プロジェクトの依存関係を分析し、セキュリティ脆弱性や更新推奨を報告。

### ユースケース
- セキュリティ監査
- 依存パッケージの棚卸し
- アップデート計画の作成

### コマンド
```
/dependency-check [--security] [--outdated] [--unused]
```

### 機能
- npm/yarn/pnpm, pip, go mod対応
- 既知の脆弱性チェック (CVE)
- 非推奨パッケージの検出
- 未使用依存関係の特定
- アップデート影響度の評価

---

## 6. commit-lint - コミットメッセージ検証プラグイン

### 概要
コミットメッセージがConventional Commitsなどの規約に従っているか検証。

### ユースケース
- コミット規約の強制
- CHANGELOGの自動生成準備
- チーム開発での統一

### コマンド
```
/commit-lint [--fix] [--format=conventional|angular|custom]
```

### 機能
- コミットメッセージのフォーマット検証
- type, scope, subjectの妥当性チェック
- 修正提案の自動生成
- プロジェクト固有ルールのサポート

---

## 7. api-doc - API ドキュメント生成プラグイン

### 概要
コードからAPIドキュメントを自動生成。

### ユースケース
- REST APIの仕様書作成
- 内部APIのドキュメント化
- OpenAPI/Swagger出力

### コマンド
```
/api-doc <path> [--format=markdown|openapi|html]
```

### 機能
- エンドポイントの自動検出
- リクエスト/レスポンス型の抽出
- サンプルリクエストの生成
- OpenAPI 3.0形式での出力

---

## 8. migration-helper - マイグレーション支援プラグイン

### 概要
フレームワークやライブラリのバージョン移行を支援。

### ユースケース
- メジャーバージョンアップ
- フレームワーク移行
- 破壊的変更への対応

### コマンド
```
/migration-helper <from-version> <to-version> [--dry-run]
```

### 機能
- 破壊的変更の影響分析
- 必要な修正箇所の特定
- 移行手順の生成
- 自動修正可能な箇所の変換

---

## 9. env-setup - 環境セットアップヘルパー

### 概要
プロジェクトの開発環境セットアップを自動化。

### ユースケース
- 新規メンバーのオンボーディング
- 環境の再構築
- CI/CD環境との整合性確認

### コマンド
```
/env-setup [--check] [--fix] [--export]
```

### 機能
- 必要なツール・バージョンの確認
- 環境変数の設定ガイド
- .env.exampleからの.env生成支援
- Docker環境のセットアップ
- トラブルシューティングガイド

---

## 10. git-workflow - Gitワークフロー支援プラグイン

### 概要
チームのGitワークフローに沿った操作を支援。

### ユースケース
- ブランチ戦略の遵守
- コンフリクト解決支援
- リリース準備

### コマンド
```
/git-workflow <action> [options]
```

### アクション
- `start-feature <name>` - フィーチャーブランチ作成
- `sync` - mainとの同期
- `resolve-conflicts` - コンフリクト解決支援
- `prepare-release` - リリース準備
- `hotfix <name>` - ホットフィックスブランチ作成

---

## 実装優先度

| プラグイン | 優先度 | 理由 |
|-----------|-------|------|
| code-review | 高 | 日常的に使用頻度が高い |
| test-gen | 高 | テスト作成の効率化に直結 |
| debug-helper | 高 | デバッグ時間の短縮 |
| dependency-check | 中 | セキュリティ対策として重要 |
| refactor-suggest | 中 | 技術的負債の可視化 |
| git-workflow | 中 | チーム開発での標準化 |
| api-doc | 低 | プロジェクト依存度が高い |
| commit-lint | 低 | 既存ツールで代替可能 |
| migration-helper | 低 | 使用頻度が限定的 |
| env-setup | 低 | プロジェクト固有設定が多い |

---

## 追加検討中のアイデア

### performance-audit
パフォーマンスボトルネックの分析と改善提案

### accessibility-check
Webアプリのアクセシビリティ検証

### i18n-helper
国際化対応の支援（翻訳キー抽出、未翻訳検出）

### schema-sync
DBスキーマとTypeScript型の同期確認

### changelog-gen
Git履歴からCHANGELOGを自動生成
