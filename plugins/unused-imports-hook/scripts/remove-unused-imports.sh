#!/bin/bash

# remove-unused-imports.sh
# ステージングされたファイルから未使用のimportを削除するスクリプト
#
# 対応言語:
# - TypeScript/JavaScript (.ts, .tsx, .js, .jsx): eslint + eslint-plugin-unused-imports
# - Python (.py): autoflake または ruff
# - Go (.go): goimports

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ステージングされたファイルを取得
get_staged_files() {
    git diff --cached --name-only --diff-filter=ACM
}

# TypeScript/JavaScript ファイルの処理
process_ts_js() {
    local files=("$@")

    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi

    log_info "TypeScript/JavaScript ファイルの未使用import削除中..."

    # eslint が利用可能かチェック
    if command -v npx &> /dev/null && [ -f "node_modules/.bin/eslint" ]; then
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                log_info "  処理中: $file"
                npx eslint --fix --rule '{"@typescript-eslint/no-unused-vars": "off", "unused-imports/no-unused-imports": "error"}' "$file" 2>/dev/null || true
            fi
        done
    # biome が利用可能かチェック
    elif command -v npx &> /dev/null && [ -f "node_modules/.bin/biome" ]; then
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                log_info "  処理中: $file"
                npx biome check --write --unsafe "$file" 2>/dev/null || true
            fi
        done
    else
        log_warn "eslint または biome が見つかりません。手動でインストールしてください:"
        log_warn "  npm install -D eslint eslint-plugin-unused-imports @typescript-eslint/eslint-plugin"
        log_warn "  または: npm install -D @biomejs/biome"
        return 1
    fi

    log_success "TypeScript/JavaScript ファイルの処理完了"
}

# Python ファイルの処理
process_python() {
    local files=("$@")

    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Python ファイルの未使用import削除中..."

    # ruff が利用可能かチェック (推奨)
    if command -v ruff &> /dev/null; then
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                log_info "  処理中: $file"
                ruff check --fix --select F401,F811 "$file" 2>/dev/null || true
            fi
        done
    # autoflake が利用可能かチェック
    elif command -v autoflake &> /dev/null; then
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                log_info "  処理中: $file"
                autoflake --in-place --remove-all-unused-imports "$file" 2>/dev/null || true
            fi
        done
    else
        log_warn "ruff または autoflake が見つかりません。手動でインストールしてください:"
        log_warn "  pip install ruff  # 推奨"
        log_warn "  または: pip install autoflake"
        return 1
    fi

    log_success "Python ファイルの処理完了"
}

# Go ファイルの処理
process_go() {
    local files=("$@")

    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Go ファイルの未使用import削除中..."

    # goimports が利用可能かチェック
    if command -v goimports &> /dev/null; then
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                log_info "  処理中: $file"
                goimports -w "$file" 2>/dev/null || true
            fi
        done
    else
        log_warn "goimports が見つかりません。手動でインストールしてください:"
        log_warn "  go install golang.org/x/tools/cmd/goimports@latest"
        return 1
    fi

    log_success "Go ファイルの処理完了"
}

# メイン処理
main() {
    log_info "未使用import削除フックを実行中..."

    # ステージングされたファイルを取得
    local staged_files
    staged_files=$(get_staged_files)

    if [ -z "$staged_files" ]; then
        log_info "ステージングされたファイルがありません"
        exit 0
    fi

    # ファイルを言語別に分類
    local ts_js_files=()
    local python_files=()
    local go_files=()

    while IFS= read -r file; do
        case "$file" in
            *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs)
                ts_js_files+=("$file")
                ;;
            *.py)
                python_files+=("$file")
                ;;
            *.go)
                go_files+=("$file")
                ;;
        esac
    done <<< "$staged_files"

    # 各言語のファイルを処理
    local has_error=0

    if [ ${#ts_js_files[@]} -gt 0 ]; then
        process_ts_js "${ts_js_files[@]}" || has_error=1
    fi

    if [ ${#python_files[@]} -gt 0 ]; then
        process_python "${python_files[@]}" || has_error=1
    fi

    if [ ${#go_files[@]} -gt 0 ]; then
        process_go "${go_files[@]}" || has_error=1
    fi

    # 変更があったファイルを再ステージング
    log_info "変更されたファイルを再ステージング中..."
    for file in "${ts_js_files[@]}" "${python_files[@]}" "${go_files[@]}"; do
        if [ -f "$file" ]; then
            git add "$file"
        fi
    done

    if [ $has_error -eq 0 ]; then
        log_success "未使用import削除フック完了"
    else
        log_warn "一部のファイルは処理できませんでした（ツール未インストール）"
    fi

    exit 0
}

main "$@"
