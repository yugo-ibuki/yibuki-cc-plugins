---
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
description: プログラミング言語の概念を公式ドキュメントから学習し、他言語との比較も含めて解説
argument-hint: <言語名> [トピック] [--compare <比較言語1,言語2,...>]
---

## 参照スキル

- `skills/doc-lookup/SKILL.md` - 公式ドキュメント検索・取得
- `skills/concept-explainer/SKILL.md` - 重要概念の抽出・解説

## コマンド概要

新しいプログラミング言語を学ぶ際に、公式ドキュメントから重要な概念を抽出し、以下を含めて解説します：

1. **公式ドキュメントからの情報取得**
2. **重要な概念の抽出と解説**
3. **他言語との比較**（既知の言語と比較してイメージしやすく）
4. **参照ドキュメントのリンク**

## 実行フロー

### Step 1: 引数の解析

```
/learn-lang rust ownership --compare javascript,python
```

| 引数 | 説明 | 例 |
|------|------|-----|
| 言語名 | 学習したい言語 | `rust`, `go`, `kotlin` |
| トピック | 特定のトピック（任意） | `ownership`, `goroutine`, `coroutine` |
| --compare | 比較対象の言語（カンマ区切り） | `javascript,python` |

### Step 2: 公式ドキュメントの検索・取得

`skills/doc-lookup/SKILL.md` を使用：

1. Context7 MCPで言語のライブラリIDを解決
2. 指定トピックに関連するドキュメントを取得
3. 取得できない場合はWebSearchでフォールバック

### Step 3: 重要概念の抽出・解説

`skills/concept-explainer/SKILL.md` を使用：

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
/learn-lang rust
```
→ Rustの基本概念（所有権、借用、ライフタイム等）を解説

### 特定トピックの学習

```
/learn-lang go goroutine
```
→ Goのgoroutineについて詳しく解説

### 他言語との比較付き

```
/learn-lang kotlin coroutine --compare javascript,python
```
→ KotlinのCoroutineをJavaScript (async/await) とPython (asyncio) と比較

### 複数の比較言語

```
/learn-lang rust error-handling --compare go,java,typescript
```
→ Rustのエラーハンドリングを複数言語と比較

## 対応言語（例）

| 言語 | Context7 ID例 | 主なトピック |
|------|---------------|--------------|
| Rust | /rust-lang/rust | ownership, borrowing, lifetime, traits |
| Go | /golang/go | goroutine, channel, interface, error-handling |
| Kotlin | /jetbrains/kotlin | coroutine, null-safety, extension-functions |
| TypeScript | /microsoft/typescript | type-system, generics, decorators |
| Python | /python/cpython | async, type-hints, decorators |
| Swift | /apple/swift | optionals, protocols, memory-management |

## 比較対象言語のデフォルト

比較言語が指定されない場合、以下の優先順位でデフォルト比較言語を選択：

1. **ユーザーのコードベースから推測**（package.json, go.mod, Cargo.toml等を確認）
2. **一般的な組み合わせ**：
   - Rust → JavaScript/TypeScript, Python, C++
   - Go → Python, Java, JavaScript
   - Kotlin → Java, Swift, TypeScript
   - Swift → Kotlin, TypeScript, Objective-C

## 注意事項

- ドキュメント取得に時間がかかる場合があります
- 最新のドキュメントはContext7経由で取得されます
- WebSearchはフォールバックとして使用されます
- 参照リンクは可能な限り公式ドキュメントを優先します
