---
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(python3:*)
description: 既存の調査ドキュメントを更新
argument-hint: <ディレクトリ名>
---

## 参照スキル

- `skills/search-related-docs/SKILL.md` - 関連ドキュメント検索・特定
- `skills/load-doc-context/SKILL.md` - 既存ドキュメントの読み込み

## 実行内容

`.claude/custom-documents` 内の既存調査ドキュメントに、**新しい調査結果や発見事項**を追記します。

## 実行フロー概要

### Step 1: 更新対象の特定（スキル使用）

引数が指定されていない場合、`skills/search-related-docs.md` を使用：

1. 調査対象のキーワードやファイルパスを特定
2. `.claude/custom-documents/` 内の調査ドキュメント（`*-investigation`, `*-analysis` など）を走査
3. 最も関連度の高いドキュメントを特定
4. 候補を提示してユーザーに確認

### Step 2: 既存ドキュメントの読み込み（スキル使用）

`skills/load-doc-context.md` を使用：

1. 選択されたドキュメントを読み込み
2. 既存の調査内容を把握
3. どのセクションに追記すべきか判断

### Step 3: 新しい調査結果の追記

既存ドキュメントに新しい発見を追記。

---

## 使用方法

```bash
# 全調査ドキュメントから選択
/update-investigate-doc

# キーワードで絞り込み
/update-investigate-doc auth

# 直接指定
/update-investigate-doc auth-system-investigation
```

## 追記対象セクション

調査ドキュメントの以下のセクションに追記：

| セクション | 追記内容 |
|------------|----------|
| 実装の構造 | 新しく発見したファイルや依存関係 |
| コードの動作 | 追加で理解した処理フロー |
| 発見事項 | 新しい設計パターンや注意点 |
| コード例 | 追加の重要なコードスニペット |
| 次のステップ | 更新された未調査領域 |

## 追記形式

新しい内容には日付を付けて追記：

```markdown
### 発見事項

#### 設計パターン
- シングルトンパターンを使用（SessionManager）

#### 追加発見（2024-11-22）
- ファクトリパターンも併用していることを確認
- SessionManager は UserFactory と連携
```

## 動作フロー

1. **対象ドキュメントの選択**
   - 引数またはインタラクティブ選択
   - 調査ドキュメント（`*-investigation`, `*-analysis`）を優先表示

2. **既存内容の解析**
   - 現在の調査範囲を把握
   - 各セクションの内容を確認

3. **追記内容の確認**
   - 新しい調査結果をユーザーから聴取
   - または現在のセッションの会話から抽出

4. **ドキュメント更新**
   - 適切なセクションに追記
   - 日付スタンプを付与

5. **HTML再生成**
   ```bash
   python plugins/custom-doc/scripts/markdown-to-html.py .claude/custom-documents/[ディレクトリ名]/
   ```

## 注意点

- 既存の調査内容は保持し、新しい発見のみ追記
- 矛盾する情報がある場合は、既存内容を訂正（訂正日を明記）
- 「次のステップ」セクションは調査完了に応じて更新
- 大幅な構造変更が必要な場合は、新規ドキュメント作成を提案
