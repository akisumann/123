#!/usr/bin/env python3
"""場所×キャラ対応マップ(72)から「誰がどの店・施設にいるか」を読み取るモジュール。

`world/crossroad/72_place_character_map.md`の
  ・区画ごとの`### 施設`の常駐者(ファイル番号のリンクで照合)  → 持ち場
  ・「行きつけの店」「宿泊」の一覧(短い呼び名で照合)          → 行きつけ・寝床
を抽出し、`tools/day_plan.py`が区画より細かい粒度で人を配置できるようにする。

単体で実行すると、抽出結果(施設と常連の対応)を一覧できる:
    python3 tools/venue_map.py
    python3 tools/venue_map.py --who ミルカ
"""
from __future__ import annotations
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_FILE = os.path.join(ROOT, "world", "crossroad", "72_place_character_map.md")
NPC_DIR = os.path.join(ROOT, "characters", "npcs")

DISTRICTS = ["中央区", "北区", "東区", "南区", "西区", "下水道"]

# 店・施設の種別ごとの、時間帯の当たり具合(その刻にそこへ人がいるか)
SLOT_WEIGHT = {
    "深夜酒場": {"未明": 3, "朝": 0, "昼": 0, "夕": 1, "宵": 4, "夜半": 5},
    "酒場":     {"未明": 0, "朝": 0, "昼": 1, "夕": 4, "宵": 4, "夜半": 1},
    "茶屋":     {"未明": 0, "朝": 3, "昼": 3, "夕": 2, "宵": 0, "夜半": 0},
    "宿":       {"未明": 5, "朝": 1, "昼": 0, "夕": 1, "宵": 1, "夜半": 4},
    "夜の場":   {"未明": 3, "朝": 0, "昼": 0, "夕": 1, "宵": 5, "夜半": 4},
    "持ち場":   {"未明": 1, "朝": 4, "昼": 5, "夕": 3, "宵": 1, "夜半": 1},
    "昼の職場": {"未明": 0, "朝": 4, "昼": 5, "夕": 3, "宵": 0, "夜半": 0},
}
# 夜が本番の施設(歓楽・興行・賭博)
NIGHT_VENUES = ("娼館", "コロッセオ", "カジノ", "万象座", "劇場", "歓楽")
# 日が暮れれば閉まる場所。夜も人がいるのは病院・黒針会・裏路地・下水道・廃研究施設など
DAY_ONLY = ("学校", "工房", "庁舎", "門", "ギルド", "浄化院", "サークル",
            "広場", "市場", "商業組合", "練兵場", "洗濯場")


def npc_names() -> dict[str, list[str]]:
    """ファイル番号 → その人物を指す呼び名(本名・読み・短縮)。"""
    out: dict[str, list[str]] = {}
    for fn in sorted(os.listdir(NPC_DIR)):
        if not fn.endswith(".md"):
            continue
        num = fn.split("_")[0]
        head = open(os.path.join(NPC_DIR, fn), encoding="utf-8").readline().lstrip("# ").strip()
        names = [head]
        m = re.match(r"^(.+?)[(（](.+?)[)）]", head)   # 「小夜(さよ)」
        if m:
            names = [m.group(1), m.group(2)]
        names.append(head.split("・")[0])              # 「クラリス・ヴァイスフェルト」→ クラリス
        out[num] = sorted(set(n for n in names if n), key=len, reverse=True)
    return out


def venue_kind(label: str) -> str:
    if "深夜酒場" in label:
        return "深夜酒場"
    if "酒場" in label:
        return "酒場"
    if "茶屋" in label:
        return "茶屋"
    if "宿" in label:
        return "宿"
    if any(k in label for k in NIGHT_VENUES):
        return "夜の場"
    if any(k in label for k in DAY_ONLY):
        return "昼の職場"
    return "持ち場"


def load(rows: list[dict]) -> dict[str, list[dict]]:
    """人物名 → その人が現れる場所のリスト(施設名・区画・種別)。"""
    by_num = {r["ファイル"]: r["名前"] for r in rows}
    aliases = npc_names()
    # 呼び名 → ルーティン表の名前
    alias_to_name: dict[str, str] = {}
    for num, names in aliases.items():
        if num in by_num:
            for n in names:
                alias_to_name.setdefault(n, by_num[num])
    for r in rows:
        alias_to_name.setdefault(r["名前"], r["名前"])

    text = open(MAP_FILE, encoding="utf-8").read()
    venues: dict[str, list[dict]] = {}

    def add(person: str, venue: str, district: str, kind: str):
        entry = {"施設": venue, "区画": district, "種別": kind}
        lst = venues.setdefault(person, [])
        if entry not in lst:
            lst.append(entry)

    # (1) 区画ごとの施設。常駐者はファイル番号のリンクで確実に取れる
    district = ""
    venue = ""
    in_hangout = False
    for line in text.splitlines():
        if line.startswith("## "):
            head = line[3:].strip()
            in_hangout = "行きつけ" in head or "宿・" in head
            district = next((d for d in DISTRICTS if head.startswith(d)), "")
            venue = ""
            continue
        if line.startswith("### "):
            venue = re.sub(r"[(（].*", "", line[4:]).strip()
            inner = re.search(r"《(.+?)》", venue)   # 「北門《王都門》」→「王都門」
            if inner:
                venue = inner.group(1)
            if len(venue) > 10:     # 「住宅街・共同井戸・洗濯場…」は先頭の呼び名で足りる
                venue = venue.split("・")[0]
            if "その他" in venue:   # 「宿・市場・その他」のような括りは施設ではない
                venue = ""
            continue
        if not in_hangout and district and venue and line.startswith("- "):
            for num in re.findall(r"characters/npcs/(\d+)_", line):
                if num in by_num:
                    add(by_num[num], venue, district, venue_kind(venue))
            continue

        # (2) 行きつけ・宿の早見。`- **店名**(区画・種別)…名前／名前…`
        if in_hangout and line.startswith("- **"):
            m = re.match(r"- \*\*(.+?)\*\*[(（]?([^)）]*)[)）]?(?:ほか)?…(.*)", line)
            if not m:
                continue
            shop, label, members = m.group(1), m.group(2), m.group(3)
            shop = re.sub(r"を拠点$", "", shop)
            place = next((d for d in DISTRICTS if d in label or d in shop), "")
            if not place or "その他" in shop:
                continue
            kind = venue_kind(label + shop)
            # 括弧の中にも名前が入る(「統制パーティー(水城・蒼龍…)」)ため、
            # 区切らずに呼び名を拾う。長い呼び名から先に当てて取りこぼしを防ぐ
            for alias in sorted(alias_to_name, key=len, reverse=True):
                if alias in members:
                    add(alias_to_name[alias], shop, place, kind)
    return venues


def pick_venue(person: str, district: str, slot: str, venues: dict[str, list[dict]], rng,
               slack: float = 3.0):
    """その人がその区画・その刻にいる店・施設(該当なしは空)。

    slackは「どの店にもいない(区画をただ歩いている)」側の重み。持ち場を離れない
    不動型は小さく、ふらつく者は大きく取る。
    """
    cands = [v for v in venues.get(person, []) if v["区画"] == district]
    weights = [(v["施設"], SLOT_WEIGHT[v["種別"]][slot]) for v in cands]
    weights = [(n, w) for n, w in weights if w > 0]
    if not weights:
        return ""
    total = sum(w for _, w in weights)
    x = rng.random() * (total + slack)
    for name, w in weights:
        x -= w
        if x < 0:
            return name
    return ""


def main() -> int:
    import day_plan as dp
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--who", default="", help="この人物の立ち寄り先だけ表示")
    args = ap.parse_args()
    rows = dp.load_rows()
    venues = load(rows)
    if args.who:
        for v in venues.get(args.who, []):
            print(f"{v['区画']}\t{v['施設']}\t{v['種別']}")
        if args.who not in venues:
            print(f"({args.who}の立ち寄り先は72に載っていない)")
        return 0
    by_venue: dict[tuple, list[str]] = {}
    for person, vs in venues.items():
        for v in vs:
            by_venue.setdefault((v["区画"], v["施設"], v["種別"]), []).append(person)
    for (district, venue, kind), who in sorted(by_venue.items()):
        print(f"{district}\t{venue}({kind})\t{'／'.join(who)}")
    print(f"\n施設{len(by_venue)}件 / 人物{len(venues)}人ぶんを72から抽出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
