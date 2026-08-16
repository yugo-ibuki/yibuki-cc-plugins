---
name: lang-learner
description: 公式ドキュメントを根拠にプログラミング言語の概念を調べ、コード例や他言語との比較付きで説明する。新しい言語、言語機能、構文、設計思想を学びたい依頼で使用する。
---

# Lang Learner

## 参照スキル

- `doc-lookup` - 公式ドキュメント検索・取得
- `concept-explainer` - 重要概念の抽出・解説

## 概要

新しいプログラミング言語を学ぶ際に、公式ドキュメントから重要な概念を抽出し、以下を含めて解説します：

1. **公式ドキュメントからの情報取得**
2. **重要な概念の抽出と解説**
3. **他言語との比較**（既知の言語と比較してイメージしやすく）
4. **参照ドキュメントのリンク**

## 実行フロー

### Step 1: 依頼の解析

```
RustのownershipをJavaScript、Pythonと比較して説明してください
```

| 引数 | 説明 | 例 |
|------|------|-----|
| 言語名 | 学習したい言語 | `rust`, `go`, `typescript`, `php` |
| トピック | 特定のトピック（任意） | `ownership`, `goroutine`, `coroutine` |
| --compare | 比較対象の言語（カンマ区切り） | `javascript,python` |

### Step 2: 公式ドキュメントの検索・取得

`doc-lookup` の手順を使用：

1. Context7 MCPで言語のライブラリIDを解決
2. 指定トピックに関連するドキュメントを取得
3. 取得できない場合はWebSearchでフォールバック

### Step 3: 重要概念の抽出・解説

`concept-explainer` の手順を使用：

1. ドキュメントから核となる概念を抽出
2. 各概念について以下を生成：
   - **概念の説明**
   - **なぜ重要か**
   - **コード例**
   - **他言語との比較**
   - **よくある間違い・注意点**

### Step 4: 出力生成

以下の形式で出力を生成：

```markdown
# [言語名]: [トピック]

## 📚 参照ドキュメント

| ソース | リンク |
|--------|--------|
| 公式ドキュメント | [URL] |
| Context7 Library ID | [ID] |
| その他参考 | [URL] |

## 🎯 核となる概念

### 1. [概念名]

**概要**
[概念の説明]

**なぜ重要か**
[この概念が言語設計で重視される理由]

**コード例**
```[言語]
// 例
```

**🔄 他言語との比較**

| 言語 | 対応する概念/機能 | 違い |
|------|-------------------|------|
| JavaScript | [対応概念] | [違いの説明] |
| Python | [対応概念] | [違いの説明] |

**⚠️ よくある間違い**
- [間違い1]
- [間違い2]

---

### 2. [次の概念]
...

## 💡 まとめ

### この言語の特徴
- [特徴1]
- [特徴2]

### 他言語から移行する際のポイント
- [ポイント1]
- [ポイント2]

### 次に学ぶべきトピック
1. [トピック1] - [理由]
2. [トピック2] - [理由]
```

## 使用例

### 基本的な使用

```
Rustの基本概念を教えてください
```
→ Rustの基本概念（所有権、借用、ライフタイム等）を解説

### 特定トピックの学習

```
Goのgoroutineを詳しく教えてください
```
→ Goのgoroutineについて詳しく解説

### 他言語との比較付き

```
GoのgoroutineをTypeScript、Pythonと比較してください
```
→ Goのgoroutineを TypeScript (async/await) と Python (asyncio) と比較

### 複数の比較言語

```
RustのエラーハンドリングをGo、TypeScript、PHPと比較してください
```
→ Rustのエラーハンドリングを複数言語と比較

## 対応言語（例）

| 言語 | Context7 ID例 | 主なトピック |
|------|---------------|--------------|
| Rust | /rust-lang/rust | ownership, borrowing, lifetime, traits |
| Go | /golang/go | goroutine, channel, interface, error-handling |
| TypeScript | /microsoft/typescript | type-system, generics, decorators, utility-types |
| JavaScript | /mdn/content | async, modules, prototypes |
| Python | /python/cpython | async, type-hints, decorators |
| PHP | /php/doc-en | namespaces, traits, type-declarations, fibers |

## 比較対象言語のデフォルト

比較言語が指定されない場合、以下の優先順位でデフォルト比較言語を選択：

1. **ユーザーのコードベースから推測**（package.json, go.mod, Cargo.toml等を確認）
2. **一般的な組み合わせ**：
   - Rust → TypeScript, Go, Python
   - Go → TypeScript, Python, PHP
   - TypeScript → JavaScript, Go, Python
   - JavaScript → TypeScript, Python, PHP
   - Python → TypeScript, Go, PHP
   - PHP → TypeScript, Python, Go

## 注意事項

- ドキュメント取得に時間がかかる場合があります
- 最新のドキュメントはContext7経由で取得されます
- WebSearchはフォールバックとして使用されます
- 参照リンクは可能な限り公式ドキュメントを優先します
