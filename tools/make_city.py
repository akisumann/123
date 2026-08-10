#!/usr/bin/env python3
"""クロスロード編の全部載せ(`123_city.md`)を生成する。

`123_all.md`が全設定を一本にまとめるのに対し、こちらは**街のセッションに要る分だけ**を
束ねる。他国・五龍・世界史といった「街の外の設定」を落とすことで、渡す相手の負担を
減らすのが目的。

含めるもの:
    START_HERE.md / CLAUDE.md   運用ルール(必須)
    CHARACTERS.md               NPC名簿。62人の要点を1枚で掴む入口
    rules/                      判定・戦闘・ステータス。戦闘を回すのに要る
    world/(直下)                経済・ギルド・暦・生成ルールなど、街の進行が毎回引く層
    world/crossroad/            街そのもの
    characters/                 NPC全員＋雛形

含めないもの:
    world/nations/              五大国と関連組織
    world/dragons/              五龍
    → 街の中の場面では滅多に開かない。必要になったら`123_all.md`か個別ファイルを見る。

使い方:
    python3 tools/make_city.py
"""
from __future__ import annotations
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_NAME = "123_city.md"

FRONT = ["START_HERE.md", "CLAUDE.md", "CHARACTERS.md"]

BODY_ORDER = [
    ("rules", "rules/ — ゲームルール"),
    ("world", "world/ — 経済・ギルド・暦・生成ルール(街の進行が引く層)"),
    ("world/crossroad", "world/crossroad/ — クロスロード(主舞台)"),
    ("characters", "characters/ — キャラクター雛形"),
    ("characters/npcs", "characters/npcs/ — 主要NPC"),
]

# 街の外の設定。クロスロード編には入れない。
SKIP_DIRS = {"world/nations", "world/dragons"}

EXCLUDE = set(FRONT) | {"README.md", "INDEX.md", "DIGEST.md", "PROGRESS.md",
                        "123_all.md", "123_city.md"}


def count_chars(text: str) -> int:
    return len("".join(text.split()))


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def collect_body_files():
    files = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "tools")]
        for n in fns:
            if not n.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, n), ROOT).replace(os.sep, "/")
            d = os.path.dirname(rel).replace(os.sep, "/")
            if rel in EXCLUDE or d in SKIP_DIRS:
                continue
            files.setdefault(d, []).append(rel)
    return files


def build() -> str:
    parts = [
        "# 123_city — クロスロード編(単一ファイル版)\n\n"
        "> **街のセッションに要る分だけ**を束ねた版です。中身は個別ファイルと同一。\n"
        "> 他国(`world/nations/`)と五龍(`world/dragons/`)は含めていません——街の中の場面では\n"
        "> 滅多に開かないためです。必要になったら`123_all.md`か個別ファイルを参照してください。\n"
        ">\n"
        "> **読み方**: まず「START_HERE」と「CLAUDE(運用ルール)」を読む。次に「NPC名簿」で\n"
        "> 誰がいるかを掴む。設定は目次から該当セクション(`## ▼ ファイルパス`)へジャンプして引く。\n"
        "> 頭から一字一句読み込もうとせず、必要箇所だけを取りに行くこと。\n"
    ]

    for rel in FRONT:
        parts.append(f"\n\n{'='*72}\n# 【最重要・先に読む】{rel}\n{'='*72}\n\n{read(rel)}")

    files = collect_body_files()
    toc = ["\n\n" + "=" * 72, "# 目次(クロスロード編の設定ファイル)", "=" * 72, ""]
    for key, label in BODY_ORDER:
        group = sorted(files.get(key, []))
        if not group:
            continue
        toc.append(f"\n**{label}**")
        for rel in group:
            toc.append(f"- `{rel}`")
    toc.append("\n**この版に含まれないもの**")
    toc.append("- `world/nations/` — 五大国と関連組織")
    toc.append("- `world/dragons/` — 五龍")
    parts.append("\n".join(toc))

    for key, label in BODY_ORDER:
        group = sorted(files.get(key, []))
        if not group:
            continue
        parts.append(f"\n\n# ■ {label}")
        for rel in group:
            parts.append(f"\n\n{'-'*72}\n## ▼ {rel}\n{'-'*72}\n\n{read(rel)}")

    return "".join(parts)


def main() -> None:
    text = build()
    with open(os.path.join(ROOT, OUT_NAME), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {OUT_NAME}  ({count_chars(text):,} 文字)")


if __name__ == "__main__":
    main()
