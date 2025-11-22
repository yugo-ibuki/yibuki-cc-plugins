#!/usr/bin/env python3
"""
ドキュメント選択ヘルパースクリプト
.claude/custom-document/ から対象ドキュメントを検索・選択
"""

import os
import sys
from pathlib import Path


def find_custom_document_dir():
    """現在のディレクトリから.claude/custom-document/を探す"""
    current = Path.cwd()

    # 上位ディレクトリを最大5階層まで探索
    for _ in range(5):
        candidate = current / ".claude" / "custom-document"
        if candidate.exists() and candidate.is_dir():
            return candidate

        if current.parent == current:  # ルートディレクトリに到達
            break
        current = current.parent

    return None


def get_documents(base_dir, keyword=None):
    """ドキュメントディレクトリ一覧を取得"""
    if not base_dir or not base_dir.exists():
        return []

    # ディレクトリのみを抽出（INDEX.md等のファイルは除外）
    docs = [d for d in base_dir.iterdir() if d.is_dir()]

    # キーワードで絞り込み
    if keyword:
        docs = [d for d in docs if keyword.lower() in d.name.lower()]

    # 名前でソート
    return sorted(docs, key=lambda x: x.name)


def select_interactive(docs):
    """インタラクティブな選択"""
    if not docs:
        print("ドキュメントが見つかりませんでした。", file=sys.stderr)
        return None

    # 1件のみの場合は自動選択
    if len(docs) == 1:
        print(f"✓ {docs[0].name} を選択しました", file=sys.stderr)
        return docs[0]

    # 複数ある場合はリスト表示
    print("\n以下のドキュメントが見つかりました:", file=sys.stderr)
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.name}", file=sys.stderr)

    print("\n番号を入力してください、またはキーワードで絞り込めます: ", file=sys.stderr, end='')

    try:
        choice = input().strip()

        # 番号選択
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(docs):
                return docs[idx]
            else:
                print(f"無効な番号です: {choice}", file=sys.stderr)
                return None

        # キーワード絞り込み
        filtered = [d for d in docs if choice.lower() in d.name.lower()]
        return select_interactive(filtered)

    except (EOFError, KeyboardInterrupt):
        print("\n中断しました", file=sys.stderr)
        return None


def main():
    """メイン処理"""
    # 引数からキーワードを取得
    keyword = sys.argv[1] if len(sys.argv) > 1 else None

    # custom-documentディレクトリを探す
    base_dir = find_custom_document_dir()
    if not base_dir:
        print("Error: .claude/custom-document/ が見つかりません", file=sys.stderr)
        sys.exit(1)

    # ドキュメント一覧を取得
    docs = get_documents(base_dir, keyword)

    # ドキュメントが見つからない場合
    if not docs:
        if keyword:
            print(f"'{keyword}' に一致するドキュメントが見つかりませんでした。", file=sys.stderr)
            print("全ドキュメントを表示します...\n", file=sys.stderr)
            docs = get_documents(base_dir)

        if not docs:
            print("ドキュメントが1件も存在しません。", file=sys.stderr)
            sys.exit(1)

    # インタラクティブに選択
    selected = select_interactive(docs)

    if selected:
        # 選択されたディレクトリ名を標準出力（これをBashで受け取る）
        print(selected.name)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
