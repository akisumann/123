#!/usr/bin/env python3
"""その日、街で流れている噂を機械的に組み立てるツール。

噂の種はGMが思いつくのではなく、シミュレーション上で実際に起きたこと
(`tools/day_plan.py`の配置・天候・行事、`tools/quest_board.py`の掲示)から拾う。
拾った噂は日を追って広まり、黒針会の情報屋網(`world/crossroad/51_black_needle_info_network.md`)
の通り、悪天候の日は伝達が一日遅れる。

井戸端会議・酒場の噂話・情報屋の掲示板(`world/crossroad/53_crossroad_wandering_events.md`)で
「今どんな話が出回っているか」を出す時に使う。

使い方:
    python3 tools/street_talk.py --day 8              # その日出回っている噂
    python3 tools/street_talk.py --day 8 --place 東区  # その区画に届いている噂だけ
"""
from __future__ import annotations
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import day_plan as dp  # noqa: E402
import quest_board as qb  # noqa: E402

TRACE_DAYS = 3          # 何日前の出来事まで噂として残るか(注目度3は+2日)
MAX_PER_DAY = 5         # 一日に立つ噂の上限
SPREAD_LABEL = ["まだ発生元の区画でだけ囁かれている", "いくつかの区画へ伝わり始めた", "街中に広まっている"]

# 遠出が噂になる行き先。近場の採取や街道往復は日常なので話題にならない
NOTABLE_DEST = set(dp.DUNGEON) | {"骨鳴り墓原", "王都街道"}


def home_place(row: dict) -> str:
    weights = dp.parse_weights(row["既定"])
    return max(weights, key=lambda x: x[1])[0]


def fame(row: dict) -> int:
    """注目度。0=裏稼業で噂にならないことが仕事、3=街の顔で動きが話題になる。"""
    try:
        return int(row.get("注目度") or 1)
    except ValueError:
        return 1


def events_of(day: int, rows: list[dict], by_name: dict[str, dict]) -> list[dict]:
    """その日に起きた、噂になりうる出来事。"""
    out = []
    sky = dp.weather_of(day)
    if sky == "荒天":
        out.append({"元": "街中", "話": "荒天で四大門の出入りが止まり、商隊が足止めされている。"
                                    "空咲の空輸便も飛べない"})
    for ev in dp.festivals_of(day):
        out.append({"元": "街中", "話": f"{ev.split('(')[0]}の話で持ちきり"})

    for row in rows:
        star = fame(row)
        if star == 0:
            continue  # 裏稼業の動きは噂に上がらない(上がったらその時点で失敗している)
        trip = dp.away_today(row, day, by_name)
        lead = dp.leader_of(row, by_name)
        if trip and lead["名前"] != row["名前"]:
            continue  # 組の話は代表者ぶんだけ立てる
        # 街の顔(3)の出入りは常に話題。名の知れた者(2)は遠方・危険な行き先の時だけ
        if trip and (star >= 3 or (star == 2 and trip[0] in NOTABLE_DEST)):
            members = [r["名前"] for r in rows
                       if dp.leader_of(r, by_name)["名前"] == lead["名前"]
                       and dp.away_today(r, day, by_name)]
            who = "・".join(members) if members else row["名前"]
            if trip[1]:
                out.append({"元": home_place(row), "話": f"{who}が{trip[0]}へ発った", "度": star})
            elif trip[2]:
                out.append({"元": home_place(row), "話": f"{who}が{trip[0]}から戻った", "度": star})

        # 珍しい場所で見かけられた。街の顔か、持ち場を離れないはずの者だけが話題になる
        place, note = dp.locate(row, day, "昼", by_name)
        if note == "いつもと違う" and (star >= 3 or dp.move_type(row) == "不動"):
            out.append({"元": place, "話": f"{row['名前']}が{place}にいるのを見かけた者がいる", "度": star})

    for q in qb.posted_on(day, qb.load_quests()):
        if q["ランク"] in ("B", "A", "S"):
            out.append({"元": "北区", "度": 3,
                        "話": f"ギルドに{q['ランク']}ランクの依頼「{q['名']}」が貼り出された({q['報酬']})"})

    out.sort(key=lambda e: -e.get("度", 3))
    return out[:MAX_PER_DAY]


def spread_of(start: int, day: int) -> int:
    """出来事が何段階まで広まったか。悪天候の日は伝達が進まない(51)。"""
    step = 0
    for d in range(start + 1, day + 1):
        if dp.weather_of(d) in ("荒天", "小雨〜雨"):
            continue  # 情報網の伝達が遅れる
        step += 1
    return min(step, len(SPREAD_LABEL) - 1)


def render(day: int, place_filter: str = "") -> str:
    rows = dp.load_rows()
    by_name = {r["名前"]: r for r in rows}
    cal = dp.calendar_of(day)
    out = ["=" * 60,
           f"街の噂({day}日目)  {cal['表記']}／空模様:{dp.weather_of(day)}",
           "=" * 60]

    buckets: dict[int, list[str]] = {}
    for start in range(max(1, day - TRACE_DAYS - 2 + 1), day + 1):
        level = spread_of(start, day)
        for ev in events_of(start, rows, by_name):
            # 古い話は忘れられる。街の顔の話だけ少し長く残る
            if day - start >= TRACE_DAYS + (2 if ev.get("度", 3) >= 3 else 0):
                continue
            if place_filter and ev["元"] not in ("街中", place_filter) and level < 2:
                continue
            age = "今日の話" if start == day else f"{day - start}日前"
            line = f"- {ev['話']}({age}・{ev['元']}発)"
            if line not in buckets.setdefault(level, []):
                buckets[level].append(line)

    for level in sorted(buckets, reverse=True):
        out.append(f"\n【{SPREAD_LABEL[level]}】")
        out += buckets[level]

    if not buckets:
        out.append("\n(語られるほどの出来事がない。世間話・軽い手伝い程度の場面で十分)")

    out.append("""
【使い方】
- 井戸端(東区の共同井戸)、酒場・茶屋(`world/crossroad/49_crossroad_dining.md`)、情報屋の掲示板
  (`world/crossroad/51_black_needle_info_network.md`)で人が話す内容として使う。
- 広まり具合は、その日までに晴れた日数で進む。雨や荒天の日は情報網の伝達が遅れて進まない(51)。
- 噂は事実そのままとは限らない。伝聞の段階で尾ひれが付くのはGMの裁量で構わない
  (`world/crossroad/53_crossroad_wandering_events.md`の噂話の扱い)。""")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", type=int, default=1, help="作中の日付")
    ap.add_argument("--place", default="", help="この区画に届いている噂だけ")
    args = ap.parse_args()
    print(render(args.day, args.place))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
