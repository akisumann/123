#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""巡穣祭の料理大会(`world/crossroad/47_crossroad_harvest_festival.md`)を引く。

巡穣祭は月に一度・年12回(`world/70_calendar_and_climate.md`)。その催しの一つ
「料理品評会」を、飛び入り参加の大会として回すためのツール。

  出場者も腕前も、その場で乱数で決まる。

**ここで出た腕前は設定にならない。** 街の誰にも「料理」のステータスもスキルも
無いので(唯一の例外はマリナの家事全般Lv3)、大会に出た者の腕は毎回この場で
振り直される。先月の優勝者が今月は最下位でも、何も矛盾しない。**結果を
characters/ へ書き戻さないこと。**

出場者は「料理をしなさそうな者」から引く。除外は二人だけで、理由は設定上
参加が成立しないため(アイアンくん=意思が無い、豊根=移動不可)。

使い方:
    python3 tools/cook_off.py                 # 今日(session_day.txt)の月の大会
    python3 tools/cook_off.py --day 45        # 45日目の属する月の大会
    python3 tools/cook_off.py --crop 芋       # 主役作物を指定する
    python3 tools/cook_off.py --entrants 6    # 出場者数を指定する(既定は4〜6の乱数)
"""
from __future__ import annotations
import argparse
import hashlib
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTINE_FILE = os.path.join(ROOT, "tools", "routines.tsv")
DAY_FILE = os.path.join(ROOT, "tools", "session_day.txt")

# ランク→ダイス面数(`rules/02_status_system.md`)
FACES = {"S": 7, "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "F": 1}
# 腕前の出やすさ。料理をしない者ばかりなので中位に寄せ、S と F を稀にする。
RANK_WEIGHTS = {"S": 1, "A": 2, "B": 3, "C": 5, "D": 5, "E": 3, "F": 2}
RANKS = list(FACES.keys())

# 主役になりやすい作物(`world/crossroad/47_crossroad_harvest_festival.md`)
CROPS = ["芋", "豆", "玉ねぎ", "ピーマン", "南瓜", "蕪",
         "葉物野菜", "林檎", "葡萄", "香草", "穀物"]

# 設定上、大会に出られない二人
EXCLUDE = {
    "アイアンくん": "意思が無い(`characters/npcs/30_ultimate_patchwork_iron_kun.md`)",
    "豊根": "本体が移動不可(`characters/npcs/56_toyone.md`)",
}

MOTIVES = [
    "なんとなく気が向いた",
    "誘われて断りきれなかった",
    "酔った勢いで名前を書いた",
    "賞品(主役作物の詰め合わせ)目当て",
    "去年負けた意地",
    "何の大会か分かっていない",
    "人数合わせで引っ張られた",
    "見物に来ただけのはずだった",
]

AXES = [
    "見た目", "味", "量", "独創", "香り", "食感", "盛り付け", "後片付け",
]

MISHAPS = [
    "途中で主役作物を切らした",
    "火加減を一度も見なかった",
    "味見を最後までしなかった",
    "隣の出場者の材料を使った",
    "皿が足りず鍋のまま出した",
    "完成が締切に間に合わなかった",
]


def rng(*parts) -> random.Random:
    """入力から決まる固定乱数(実行のたびに変わらない)。"""
    key = "|".join(str(p) for p in parts)
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]
    return random.Random(int(digest, 16))


def today() -> int:
    try:
        with open(DAY_FILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 1


def roster() -> list[str]:
    """routines.tsv から住人名を読む(day_plan.py と同じ表)。"""
    names = []
    with open(ROUTINE_FILE, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.startswith("#") or not line.strip():
                continue
            name = line.split("\t")[0].strip()
            if name == "名前":
                continue
            names.append(name)
    return names


def month_of(day: int) -> int:
    """1年=12ヶ月×30日(`world/70_calendar_and_climate.md`)。"""
    return ((day - 1) // 30) % 12 + 1


def festival_day(day: int) -> int:
    """その月の巡穣祭の開催日(1〜30)。収穫状況で前後するので月ごとに乱数。"""
    year = (day - 1) // 360
    return rng("harvest", year, month_of(day)).randint(8, 26)


def draw(day: int, crop: str | None, n: int | None) -> dict:
    month = month_of(day)
    year = (day - 1) // 360 + 1
    r = rng("cookoff", year, month)

    crop = crop or r.choice(CROPS)
    pool = [x for x in roster() if x not in EXCLUDE]
    n = n or r.randint(4, 6)
    picked = r.sample(pool, min(n, len(pool)))

    entries = []
    for who in picked:
        er = rng("cookoff-entry", year, month, who)
        rank = er.choices(RANKS, weights=[RANK_WEIGHTS[x] for x in RANKS])[0]
        faces = FACES[rank]
        rolls = [er.randint(1, faces) for _ in range(3)]
        entries.append({
            "who": who,
            "motive": er.choice(MOTIVES),
            "rank": rank,
            "faces": faces,
            "rolls": rolls,
            "score": sum(rolls),
            "axis": er.choice(AXES),
            "mishap": er.choice(MISHAPS) if er.random() < 0.35 else None,
        })
    entries.sort(key=lambda e: (-e["score"], e["who"]))
    return {
        "year": year, "month": month, "crop": crop,
        "fday": festival_day(day), "entries": entries,
    }


def render(d: dict) -> str:
    L = []
    L.append("=" * 60)
    L.append(f"巡穣祭 料理大会　{d['year']}年 {d['month']}の月 {d['fday']}日"
             f"／主役作物:{d['crop']}")
    L.append("=" * 60)
    L.append("")
    L.append("【この結果は設定にならない】出場者の腕前は毎回この場で振り直される。")
    L.append("characters/ へ書き戻さないこと。")
    L.append("")
    L.append(f"出場 {len(d['entries'])}名(飛び入り)")
    L.append("")
    prev, place = None, 0
    for i, e in enumerate(d["entries"], 1):
        if e["score"] != prev:
            place, prev = i, e["score"]
        crown = "★" if place == 1 else "  "
        tie = "(同点)" if [x["score"] for x in d["entries"]].count(e["score"]) > 1 else ""
        L.append(f"{crown}{place}位{tie}  {e['who']}")
        L.append(f"      腕前:{e['rank']}(3d{e['faces']})　"
                 f"出目 {'+'.join(str(x) for x in e['rolls'])} = **{e['score']}**")
        L.append(f"      持ち味:{e['axis']}　／　参加理由:{e['motive']}")
        if e["mishap"]:
            L.append(f"      やらかし:{e['mishap']}")
        L.append("")
    top = d["entries"][0]
    L.append("-" * 60)
    L.append(f"優勝:{top['who']}({top['score']}点／{top['axis']}で取った)")
    L.append("")
    L.append("描写の指針:")
    L.append("- 出た数字が全て。腕前ランクは料理の腕だけを指し、その人の他の能力とは無関係。")
    L.append("- ただし**なぜそうなったかは本人のステータスで説明してよい**")
    L.append("  (DEX:Aなら手際で、INT:Eなら勘で、HP:Sなら力技で、という色付け)。")
    L.append("- 低く出た者を物語都合で救わない。高く出た者に理由を後付けしない。")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description="巡穣祭の料理大会を引く")
    ap.add_argument("--day", type=int, default=None,
                    help="作中の日付(省略で session_day.txt の今日)")
    ap.add_argument("--crop", default=None, help="主役作物を指定する")
    ap.add_argument("--entrants", type=int, default=None, help="出場者数(既定4〜6)")
    a = ap.parse_args()
    print(render(draw(a.day if a.day is not None else today(), a.crop, a.entrants)))


if __name__ == "__main__":
    main()
