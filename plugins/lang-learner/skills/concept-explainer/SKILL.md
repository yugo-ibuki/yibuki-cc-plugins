---
name: concept-explainer
description: ドキュメントから重要な概念を抽出し、他言語との比較を含めて解説するスキル。/learn-lang コマンドで使用。学習者が理解しやすいように、既知の言語との対比を重視。
allowed-tools:
  - Read
  - WebSearch
  - mcp__context7__query-docs
---

# concept-explainer スキル

プログラミング言語の概念を、他言語との比較を含めて解説するための内部スキル。

## 目的

`/learn-lang` コマンド実行時に：
1. ドキュメントから核となる概念を抽出
2. 各概念を他言語と比較して解説
3. 学習者が理解しやすい形式で出力

## 概念抽出のアプローチ

### Phase 1: 核となる概念の特定

ドキュメントから以下を抽出：

```yaml
concept_extraction:
  primary_concepts:
    - name: "[概念名]"
      importance: high | medium | low
      unique_to_language: true | false
      related_concepts: []

  language_specific_features:
    - "[その言語特有の機能]"

  common_patterns:
    - "[一般的なパターン]"
```

### Phase 2: 他言語との対応関係マッピング

```yaml
cross_language_mapping:
  rust:
    ownership:
      javascript: "参照とガベージコレクション（GC任せ）"
      python: "参照カウント + GC"
      cpp: "スマートポインタ (unique_ptr, shared_ptr)"
      go: "GC（所有権概念なし）"

    borrowing:
      javascript: "なし（すべて参照コピー）"
      python: "なし（オブジェクト参照のみ）"
      cpp: "参照（&）とconst参照"

  go:
    goroutine:
      javascript: "async/await + Promise"
      python: "asyncio / threading"
      java: "Thread / ExecutorService / Virtual Threads"
      kotlin: "Coroutine"

    channel:
      javascript: "なし（Promise/Observableで代用）"
      python: "queue.Queue / asyncio.Queue"
      java: "BlockingQueue"
```

### Phase 3: 解説生成

各概念について以下の構造で解説を生成：

```markdown
### [概念名]

**概要**
[1-2文で概念を説明]

**なぜこの言語に必要か**
[言語設計の背景、解決しようとしている問題]

**コード例**
```[言語]
// 良い例
[コード]

// 悪い例（よくある間違い）
[コード] // ← ここがダメ
```

**🔄 他言語との比較**

| 言語 | 対応する概念 | 違い |
|------|-------------|------|
| [言語1] | [概念/機能] | [違いの説明] |
| [言語2] | [概念/機能] | [違いの説明] |

**💡 既知の言語から理解するコツ**
- [言語X]経験者: [こう考えるとわかりやすい]
- [言語Y]経験者: [こう考えるとわかりやすい]

**⚠️ よくある間違い**
1. [間違い1]: [なぜ間違いか、正しい方法]
2. [間違い2]: [なぜ間違いか、正しい方法]

**📚 参考リンク**
- [公式ドキュメント](URL)
- [関連チュートリアル](URL)
```

## 比較パターンテンプレート

### メモリ管理の比較

| 言語 | 方式 | 特徴 |
|------|------|------|
| Rust | 所有権システム | コンパイル時にメモリ安全性を保証 |
| C++ | 手動 + スマートポインタ | 柔軟だが責任はプログラマ |
| Go | GC | シンプルだがSTW発生 |
| Java | GC | 成熟したGC、複数アルゴリズム |
| JavaScript | GC | イベントループとの統合 |
| Python | 参照カウント + GC | 循環参照対策あり |

### 並行処理の比較

| 言語 | 主な方式 | 特徴 |
|------|----------|------|
| Go | goroutine + channel | 軽量、CSPモデル |
| Rust | async/await + tokio | ゼロコスト抽象化 |
| JavaScript | async/await + Promise | シングルスレッド、イベントループ |
| Python | asyncio / threading | GILの制約あり |
| Kotlin | Coroutine | 構造化並行性 |
| Java | Virtual Threads (21+) | 軽量スレッド |

### エラーハンドリングの比較

| 言語 | 主な方式 | 特徴 |
|------|----------|------|
| Rust | Result<T, E> + ? | 型安全、明示的 |
| Go | error返り値 | シンプル、if err != nil |
| TypeScript | try-catch + union types | 例外 + 型による安全性 |
| Java | checked/unchecked exceptions | 例外中心 |
| Swift | Result + throws | オプショナルとの統合 |
| Kotlin | 例外 + runCatching | Javaとの互換性 |

## 出力テンプレート

### 完全な出力例

```markdown
# Rust: 所有権 (Ownership)

## 📚 参照ドキュメント

| ソース | リンク |
|--------|--------|
| The Rust Book | [What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) |
| Rust by Example | [Ownership](https://doc.rust-lang.org/rust-by-example/scope/move.html) |
| Context7 | /rust-lang/rust |

## 🎯 核となる概念

### 1. 所有権 (Ownership)

**概要**
Rustでは、すべての値に「所有者」となる変数が1つだけ存在し、所有者がスコープを抜けると値は自動的に破棄されます。

**なぜRustに必要か**
- ガベージコレクタなしでメモリ安全性を実現
- コンパイル時にメモリリークや二重解放を防止
- ランタイムオーバーヘッドゼロ

**コード例**
```rust
fn main() {
    let s1 = String::from("hello");  // s1が所有者
    let s2 = s1;                      // 所有権がs2に移動（move）
    // println!("{}", s1);            // エラー！s1は無効
    println!("{}", s2);               // OK
}
```

**🔄 他言語との比較**

| 言語 | 対応する概念 | 違い |
|------|-------------|------|
| JavaScript | 参照コピー | 所有権なし、GCが管理 |
| Python | 参照カウント | オブジェクトは共有、GCが解放 |
| C++ | unique_ptr | 似た概念だがより柔軟 |
| Go | なし | GCが全自動で管理 |

**💡 既知の言語から理解するコツ**
- JavaScript経験者: `const obj = {...}` で代入すると参照がコピーされますが、Rustでは「所有権が移動」します。元の変数は使えなくなります。
- C++経験者: `std::unique_ptr` の move semantics に近いですが、Rustではデフォルト動作です。

**⚠️ よくある間違い**
1. **move後に元の変数を使う**: 所有権が移動した変数へのアクセスはコンパイルエラー
2. **関数に渡して戻ってこない**: 関数に値を渡すと所有権も移動するため、参照を使うか戻り値で返す

---

### 2. 借用 (Borrowing)
...

## 💡 まとめ

### Rustの所有権システムの特徴
- コンパイル時にメモリ安全性を保証
- 実行時オーバーヘッドなし
- 学習曲線は急だが、習得後は強力なツール

### 他言語から移行する際のポイント
- JavaScript/Python: 「すべてがコピー/共有」という発想を捨てる
- C++: スマートポインタの厳格版と考える
- Go: GCがないぶん明示的な制御が必要

### 次に学ぶべきトピック
1. **借用とライフタイム** - 所有権を移さずに値を使う方法
2. **スマートポインタ** - Rc, Arc, RefCellなど
3. **エラーハンドリング** - Result型とOption型
```

## 注意事項

- 比較は正確性を重視（曖昧な比較は避ける）
- 各言語の最新バージョンを基準にする
- 参照リンクは公式ドキュメントを優先
- コード例は実行可能なものを提供
- 「似ている」だけでなく「違い」を明確に説明
