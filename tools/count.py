#!/usr/bin/env python3
"""設定ファイルの文字数を測り、AI に渡す量を管理するためのツール。

使い方:
    python3 tools/count.py            # 全 .md の文字数を一覧表示
    python3 tools/count.py --budget   # 予算（tools/budget.txt）と照らして超過を警告

文字数の目安（ざっくり）:
    日本語は 1 文字 ≒ 0.6〜1 トークン程度。50 万文字 ≒ 30〜50 万トークン。
    → 多くの AI の実用範囲を超える。ここでは「一度に渡す塊」を小さく保つのが目的。
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 常時ロードする「正典」の推奨上限（文字）。ここを超えたら要約し直す合図。
CORE_FILES = {
    "world/canon.md": 4000,
    "world/overview.md": 2000,
    "world/rules.md": 3000,
    "ai/system-prompt.md": 3000,
    "ai/style-guide.md": 2000,
}


def count_chars(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # 空白・改行を除いた「実文字数」で数える（トークン量の目安に近い）
    return len("".join(text.split()))


def iter_md_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tools")]
        for name in sorted(filenames):
            if name.endswith(".md"):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT)
                yield rel, full


def main() -> int:
    check_budget = "--budget" in sys.argv
    rows = []
    total = 0
    core_total = 0
    over = []
    for rel, full in iter_md_files():
        n = count_chars(full)
        total += n
        limit = CORE_FILES.get(rel.replace(os.sep, "/"))
        tag = ""
        if limit is not None:
            core_total += n
            if n > limit:
                tag = f"  ⚠ 正典上限 {limit} 超過"
                over.append((rel, n, limit))
            else:
                tag = f"  (正典 / 上限 {limit})"
        rows.append((rel, n, tag))

    width = max((len(r[0]) for r in rows), default=10)
    print(f"{'ファイル'.ljust(width)}  文字数")
    print("-" * (width + 12))
    for rel, n, tag in rows:
        print(f"{rel.ljust(width)}  {n:>7,}{tag}")
    print("-" * (width + 12))
    print(f"{'合計'.ljust(width)}  {total:>7,}")
    print(f"{'うち常時ロード(正典)'.ljust(width)}  {core_total:>7,}")
    print()
    print("目安: 常時ロード分は 1 万文字以内に収めると、AI が安定して全部読めます。")

    if check_budget and over:
        print("\n⚠ 正典の上限を超えているファイルがあります。要約して圧縮してください:")
        for rel, n, limit in over:
            print(f"  - {rel}: {n:,} 文字 (上限 {limit:,})")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
