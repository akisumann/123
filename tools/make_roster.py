#!/usr/bin/env python3
"""全NPCの要点を1枚へ集めた名簿(`CHARACTERS.md`)を生成する。

60人ぶんのファイルを開かないと誰が何者か分からない状態を解消するための索引。
**手書きせず、各`characters/npcs/`から機械抽出する**ので、元ファイルを直せば
名簿も自動で追従し、二重管理にならない。

AIはまずこの1枚を読み、実際に描写する人物だけ個別ファイル(または
`tools/scene_context.py`)へ降りる、という使い方を想定している。

    python3 tools/make_roster.py
"""
from __future__ import annotations
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPC_DIR = os.path.join(ROOT, "characters", "npcs")
OUT = os.path.join(ROOT, "CHARACTERS.md")
STATS = ["HP", "MP", "ATK", "DEF", "INT", "SPD", "DEX"]
RANK_ORDER = {"SS": 8, "S": 7, "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "F": 1}


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def field(text: str, key: str) -> str:
    m = re.search(rf"(?m)^- \*{{0,2}}{key}\*{{0,2}}[：:]\s*(.+)$", text)
    return re.sub(r"\(.*", "", m.group(1)).strip() if m else ""


def stats_of(text: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r"(?m)^\|\s*(HP|MP|ATK|DEF|INT|SPD|DEX)\s*\|\s*(SS|[SABCDEF])\s*\|", text):
        out.setdefault(m.group(1), m.group(2))
    return out


def skills_of(text: str) -> list[tuple[str, int]]:
    return [(m.group(1).strip(), int(m.group(2)))
            for m in re.finditer(r"◇\s*(.+?)[\s　]+Lv(\d+)", text)]


def section(text: str, name: str) -> str:
    m = re.search(rf"(?m)^## {name}\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def haunt(text: str) -> str:
    m = re.search(r"\*\*行きつけ\*\*[：:]\s*(.+)", text)
    if not m:
        return ""
    return re.sub(r"\(`[^`]+`\)", "", m.group(1)).strip().rstrip("。")


def voice_line(text: str) -> str:
    body = section(text, "口調") or section(text, "口調:喋らない")
    if not body:
        return ""
    first = body.split("\n")[0]
    return re.sub(r"\*\*|`[^`]+`|\(`[^`]+`\)", "", first).strip()


def build() -> str:
    import day_plan as dp
    routines = {r["ファイル"]: r for r in dp.load_rows()}

    rows, blocks = [], []
    for fn in sorted(os.listdir(NPC_DIR)):
        if not fn.endswith(".md"):
            continue
        num = fn.split("_")[0]
        text = read(os.path.join(NPC_DIR, fn))
        name = text.lstrip().splitlines()[0].lstrip("# ").strip()
        nick = field(text, "通り名")
        lv = field(text, "レベル") or field(text, "レベル")
        stand = field(text, "立場") or field(text, "役割")
        stats = stats_of(text)
        top = sorted(stats.items(), key=lambda x: -RANK_ORDER.get(x[1], 0))
        strong = "・".join(f"{k}:{v}" for k, v in top[:2]) if top else "—"
        weak = f"{top[-1][0]}:{top[-1][1]}" if top else "—"
        sk = skills_of(text)
        best = "・".join(n for n, _ in sorted(sk, key=lambda x: -x[1])[:2]) if sk else "—"
        rt = routines.get(num, {})
        home = (rt.get("既定", "").split(":")[0] or "—")
        rows.append(f"| {num} | {name} | {nick or '—'} | {lv or '—'} | {home} | "
                    f"{strong} | {weak} | {best} |")
        v = voice_line(text)
        h = haunt(text)
        detail = f"**{num} {name}**({nick})　{stand}"
        if v:
            detail += f"\n　口調:{v}"
        if h:
            detail += f"\n　行きつけ:{h}"
        blocks.append(detail)

    head = """# NPC名簿(自動生成)

> **TL;DR:** 主要NPC60人の要点を1枚に集めた名簿(レベル・拠点区画・得意/不得意・看板スキル・口調・行きつけ)。

**このファイルは`tools/make_roster.py`が`characters/npcs/`から生成する。直接編集しない**
(元ファイルを直せばここも変わる)。

使い方:まずこの1枚で「誰が何者か」を掴み、実際に描写する人物だけ個別ファイルへ降りる。
描写の直前には`python3 tools/scene_context.py --chars <名前>`でステータス・スキル・口調の全文を引く。

## 一覧

| # | 名前 | 通り名 | Lv | 拠点区画 | 得意 | 不得意 | 看板スキル |
|---|---|---|---|---|---|---|---|
"""
    return (head + "\n".join(rows)
            + "\n\n## 一行プロフィール(口調と行きつけ)\n\n"
            + "\n\n".join(blocks) + "\n")


def main() -> int:
    text = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"CHARACTERS.md: {len(text):,}文字")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
