#!/usr/bin/env python3
"""123_all.md（全部載せ・単一ファイル）を生成する。

zip を読み込めない AI へ渡すためのフォールバック。全ファイルを 1 枚に結合するが、
ただ繋げるのではなく **読みやすい構造** にする:

  1. 先頭に「使い方 + 圧縮版の正典(START_HERE) + GM運用ルール(CLAUDE)」を置く
     → AI は長文でも冒頭は必ず読むので、重要な核を最初に読ませられる。
  2. 続いて「目次(全ファイル一覧)」。
  3. その後に各ファイル本体を、明確な区切り見出し付きで並べる。
     → 「## ▼ path/to/file.md」で検索・ジャンプできる。

  python3 tools/make_all.py            # → 123_all.md を生成
  python3 tools/make_all.py --name X   # → 出力ファイル名を X にする
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 先頭に「そのまま」置くファイル(この順)。以降の本体列挙では重複させない。
FRONT = ["START_HERE.md", "CLAUDE.md"]

# 本体を並べる順(index と同じ考え方)。ラベルはセクション見出しに使う。
BODY_ORDER = [
    ("rules", "rules/ — ゲームルール"),
    ("world", "world/ — 世界観の核"),
    ("world/nations", "world/nations/ — 五大国と関連組織"),
    ("world/dragons", "world/dragons/ — 五龍"),
    ("world/crossroad", "world/crossroad/ — クロスロード(主舞台)"),
    ("characters", "characters/ — キャラクター雛形"),
    ("characters/npcs", "characters/npcs/ — 主要NPC"),
]

# 本体列挙から除外(先頭に置く/生成物/作業ログは末尾に別途)
EXCLUDE = set(FRONT) | {"README.md", "INDEX.md", "DIGEST.md", "PROGRESS.md"}


def count_chars(text: str) -> int:
    return len("".join(text.split()))


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def rel_dir(rel: str) -> str:
    return os.path.dirname(rel).replace(os.sep, "/")


def collect_body_files():
    files = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "tools")]
        for n in fns:
            if not n.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, n), ROOT).replace(os.sep, "/")
            if rel in EXCLUDE or rel == OUT_NAME:
                continue
            files.setdefault(rel_dir(rel), []).append(rel)
    return files


def build() -> str:
    parts = []
    parts.append(
        "# 123_all — 全部載せ(単一ファイル版)\n\n"
        "> これは zip を読めない AI へ渡すための結合版です。中身は個別ファイルと同一。\n"
        "> **読み方**: まず下の「圧縮版の正典」と「GM運用ルール」を読む。次に「目次」で\n"
        "> 全体像を掴み、必要な設定は該当セクション(`## ▼ ファイルパス`)へジャンプして読む。\n"
        "> 長いので、頭から一字一句読み込もうとせず、目次を使って必要箇所を引くこと。\n"
    )

    # 1. 先頭ファイル(正典・運用ルール)
    for rel in FRONT:
        parts.append(f"\n\n{'='*72}\n# 【最重要・先に読む】{rel}\n{'='*72}\n\n{read(rel)}")

    # 2. 目次
    files = collect_body_files()
    toc = ["\n\n" + "="*72, "# 目次(全設定ファイル)", "="*72, ""]
    for key, label in BODY_ORDER:
        group = sorted(files.get(key, []))
        if not group:
            continue
        toc.append(f"\n**{label}**")
        for rel in group:
            toc.append(f"- `{rel}`")
    parts.append("\n".join(toc))

    # 3. 本体
    for key, label in BODY_ORDER:
        group = sorted(files.get(key, []))
        if not group:
            continue
        parts.append(f"\n\n{'#'*1} ■ {label}")
        for rel in group:
            parts.append(f"\n\n{'-'*72}\n## ▼ {rel}\n{'-'*72}\n\n{read(rel)}")

    # 4. 付録: 作業ログ
    if os.path.exists(os.path.join(ROOT, "PROGRESS.md")):
        parts.append(f"\n\n{'='*72}\n# 付録: PROGRESS.md(作業ログ・参照用)\n{'='*72}\n\n{read('PROGRESS.md')}")

    return "".join(parts)


def main() -> None:
    text = build()
    out = os.path.join(ROOT, OUT_NAME)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {OUT_NAME}  ({count_chars(text):,} 文字)")
    print("先頭に正典＋目次を配置済み。zip 非対応の AI にはこの 1 ファイルを渡す。")


if __name__ == "__main__":
    OUT_NAME = "123_all.md"
    if "--name" in sys.argv:
        OUT_NAME = sys.argv[sys.argv.index("--name") + 1]
    main()
