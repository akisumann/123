#!/usr/bin/env python3
"""リポジトリ全体を1つのJSON(`123.json`)へまとめる。

zip(展開できるAI用)・`123_all.md`(zipを読めないAI用)と並ぶ3つ目の渡し方で、
JSONを構造として食えるAI・外部ツール向け。全ファイルの中身に加えて、
`tools/routines.tsv`の生活ルーティンと、72から抽出した施設×人物の対応も
構造化して同梱するので、ツールを実行できない相手でもデータとして扱える。

    python3 tools/make_json.py            # 123.json を生成
    python3 tools/make_json.py --compact  # 改行・字下げなしで小さく
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "123.json")
SKIP_DIRS = {".git", "tools", "__pycache__"}
SKIP_FILES = {"123_all.md", "123.json"}
CANON = ["START_HERE.md", "CLAUDE.md", "INDEX.md"]


def md_files() -> list[str]:
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md") and fn not in SKIP_FILES:
                out.append(os.path.relpath(os.path.join(base, fn), ROOT))
    return sorted(out)


def tldr_of(text: str) -> str:
    m = re.search(r"(?m)^> \*\*TL;DR:\*\*\s*(.+)$", text)
    return m.group(1).strip() if m else ""


def routines() -> list[dict]:
    import day_plan as dp
    return dp.load_rows()


def venues() -> dict:
    import day_plan as dp
    import venue_map
    return venue_map.load(dp.load_rows())


def build() -> dict:
    files = []
    for path in md_files():
        text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        files.append({"path": path, "tldr": tldr_of(text),
                      "chars": len(text), "content": text})
    canon = {p: next((f["content"] for f in files if f["path"] == p), "") for p in CANON}
    return {
        "リポジトリ": "123",
        "説明": "ファンタジーTRPG世界クロスロードの設定データベース兼・正典。"
                "まず「正典」の START_HERE.md と CLAUDE.md を読み、"
                "以降は「ファイル」から場面に必要なものだけを引くこと。",
        "ファイル数": len(files),
        "総文字数": sum(f["chars"] for f in files),
        "正典": canon,
        "ファイル": files,
        "データ": {
            "生活ルーティン": routines(),
            "施設と人物": venues(),
            "説明": "生活ルーティンは tools/routines.tsv(誰がいつどの区画にいるか)、"
                    "施設と人物は 72 から抽出した店・施設ごとの顔ぶれ。"
                    "tools/day_plan.py がこれを使って日々の配置を生成する。",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--compact", action="store_true", help="字下げなしで小さく出す")
    args = ap.parse_args()
    data = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False,
                  indent=None if args.compact else 1,
                  separators=(",", ":") if args.compact else None)
    size = os.path.getsize(OUT)
    print(f"123.json: {data['ファイル数']}ファイル / {data['総文字数']:,}文字 "
          f"/ {size / 1024 / 1024:.1f}MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
