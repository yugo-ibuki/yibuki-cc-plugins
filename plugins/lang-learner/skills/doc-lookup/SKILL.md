---
name: doc-lookup
description: プログラミング言語の公式ドキュメントを検索・取得するスキル。Context7 MCPを優先し、取得できない場合はWebSearchでフォールバック。/learn-lang コマンドで使用。
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - WebSearch
  - WebFetch
---

# doc-lookup スキル

プログラミング言語の公式ドキュメントを効率的に検索・取得するための内部スキル。

## 目的

`/learn-lang` コマンド実行時に：
1. 指定された言語の公式ドキュメントを取得
2. 特定トピックに関連する情報を抽出
3. 参照リンクを収集

## ドキュメント取得フロー

### Phase 1: Context7 MCPによる取得（優先）

```
1. resolve-library-id で言語のライブラリIDを解決
2. query-docs でトピックに関するドキュメントを取得
3. 取得成功 → Phase 3 へ
4. 取得失敗 → Phase 2 へフォールバック
```

### Phase 2: WebSearch によるフォールバック

```
1. WebSearch で "[言語名] [トピック] official documentation" を検索
2. 公式サイトを優先してフィルタリング
3. WebFetch で詳細情報を取得
```

### Phase 3: 情報の構造化

取得した情報を以下の形式に構造化：

```yaml
documentation:
  language: "rust"
  topic: "ownership"
  sources:
    - type: "context7"
      library_id: "/rust-lang/rust"
      content: "[取得したドキュメント内容]"

    - type: "official"
      url: "https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html"
      title: "What is Ownership?"

    - type: "reference"
      url: "https://doc.rust-lang.org/reference/expressions.html"
      title: "Rust Reference"

  key_sections:
    - title: "Ownership Rules"
      content: "[内容]"
    - title: "Memory Safety"
      content: "[内容]"
```

## 言語別ドキュメントソース

### 主要言語の公式ドキュメント

| 言語 | 公式ドキュメント | Context7 対応 |
|------|------------------|---------------|
| Rust | doc.rust-lang.org | ✅ /rust-lang/rust |
| Go | go.dev/doc | ✅ /golang/go |
| TypeScript | typescriptlang.org/docs | ✅ /microsoft/typescript |
| JavaScript | developer.mozilla.org | ✅ /mdn/content |
| Python | docs.python.org | ✅ /python/cpython |
| PHP | php.net/manual | ✅ /php/doc-en |

### WebSearchクエリパターン

```
# 基本パターン
"[言語] [トピック] official documentation"

# 具体例
"rust ownership official documentation"
"go goroutine tutorial site:go.dev"
"typescript generics guide site:typescriptlang.org"
"php fibers tutorial site:php.net"

# 比較用
"[言語1] vs [言語2] [トピック]"
```

## 出力形式

### 成功時

```yaml
status: success
sources:
  - source: "Context7"
    library_id: "/rust-lang/rust"
    url: null

  - source: "Official Documentation"
    url: "https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html"
    title: "What is Ownership? - The Rust Programming Language"

content:
  main: "[メインコンテンツ]"
  code_examples:
    - "[コード例1]"
    - "[コード例2]"
  related_topics:
    - "borrowing"
    - "lifetimes"
```

### 失敗時（フォールバック込み）

```yaml
status: partial
warning: "Context7でのドキュメント取得に失敗しました。WebSearchの結果を使用しています。"
sources:
  - source: "WebSearch"
    url: "https://example.com/rust-ownership"
    reliability: "medium"

content:
  main: "[WebSearchからの内容]"
```

## 使用方法

### 基本的な呼び出し

```markdown
## ドキュメント取得

以下の手順でドキュメントを取得：

1. Context7 で `resolve-library-id` を実行
   - query: "[ユーザーの質問]"
   - libraryName: "[言語名]"

2. 取得したライブラリIDで `query-docs` を実行
   - libraryId: "[取得したID]"
   - query: "[トピック]"

3. 結果を構造化して返却
```

### コマンドへの組み込み

```markdown
## /learn-lang での使用

1. `skills/doc-lookup/SKILL.md` を参照
2. 言語名とトピックを渡してドキュメントを取得
3. 取得結果を `skills/concept-explainer/SKILL.md` に渡す
```

## エラーハンドリング

| エラー | 対処 |
|--------|------|
| Context7 IDが見つからない | WebSearchにフォールバック |
| ドキュメントが空 | 別のクエリで再試行 |
| タイムアウト | WebSearchにフォールバック |
| 言語が未対応 | WebSearchで直接検索 |

## 注意事項

- Context7の呼び出しは1つの質問につき最大3回まで
- WebFetchは公式ドキュメントのみを対象とする
- 取得したURLは必ず出力に含める
- 著作権に配慮し、引用は適切な範囲に留める
