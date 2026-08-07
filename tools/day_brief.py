#!/usr/bin/env python3
"""その日の街を一枚にまとめるツール(暦・天候・行事・配置・掲示板・噂)。

`day_plan.py`・`quest_board.py`・`street_talk.py`を個別に叩く代わりに、一日ぶんを
一度に出す。`--json`を付けると機械可読な形で出るので、**Pythonを実行できないAIへ
貼り付けて渡す**用途にも使える(実行できるAIはツールを直接叩けばよい)。

使い方:
    python3 tools/day_brief.py --day 8              # 一日ぶんを読み物として
    python3 tools/day_brief.py --day 8 --time 宵    # その刻だけ
    python3 tools/day_brief.py --day 8 --json       # JSONで出す(他のAIへ渡す用)
"""
from __future__ import annotations
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import day_plan as dp  # noqa: E402
import quest_board as qb  # noqa: E402
import street_talk as st  # noqa: E402
import venue_map  # noqa: E402


def placement(day: int, slots: list[str]) -> dict:
    rows = dp.load_rows()
    by_name = {r["名前"]: r for r in rows}
    venues = venue_map.load(rows)
    out: dict[str, dict] = {}
    for slot in slots:
        here: dict[str, dict[str, list[str]]] = {}
        for row in rows:
            place, note = dp.locate(row, day, slot, by_name)
            entry = {"名前": row["名前"]}
            if note:
                entry["注記"] = note
            route = dp.route_of(row, day, slot, place)
            if route:
                entry["巡回先"] = route
            spot = ""
            if place in dp.IN_TOWN:
                slack = 1.0 if dp.move_type(row) == "不動" else 3.0
                spot = venue_map.pick_venue(row["名前"], place, slot, venues,
                                            dp.rng("venue", day, slot, row["名前"]), slack)
            here.setdefault(place, {}).setdefault(spot or "(区画内)", []).append(entry)
        out[slot] = here
    return out


def brief(day: int, slots: list[str]) -> dict:
    cal = dp.calendar_of(day)
    board = qb.board_of(day, qb.load_quests())
    rows = dp.load_rows()
    by_name = {r["名前"]: r for r in rows}

    rumors = []
    for start in range(max(1, day - st.TRACE_DAYS - 1), day + 1):
        level = st.spread_of(start, day)
        for ev in st.events_of(start, rows, by_name):
            if day - start >= st.TRACE_DAYS + (2 if ev.get("度", 3) >= 3 else 0):
                continue
            rumors.append({"話": ev["話"], "発生元": ev["元"],
                           "何日前": day - start, "広まり": st.SPREAD_LABEL[level]})

    return {
        "日付": day,
        "暦": {k: cal[k] for k in ("年", "月", "日", "旬", "表記")},
        "天候": dp.weather_of(day),
        "行事": [e.split("(")[0] for e in dp.festivals_of(day)],
        "配置": placement(day, slots),
        "掲示板": [{"ランク": q["ランク"], "依頼名": q["名"], "舞台": q["舞台"],
                    "推奨人数": q["人数"], "報酬": q["報酬"], "内容": q["内容"],
                    "掲示日数": q["経過"] + 1} for q in board],
        "噂": rumors,
        "注記": "機械生成(tools/day_brief.py)。人物のステータス・スキル・口調は"
                "characters/npcs/、店の詳細は world/crossroad/49・72 を参照すること。",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", type=int, default=None)
    ap.add_argument("--time", default="", help=f"時間帯({'/'.join(dp.SLOTS)})。省略で一日ぶん")
    ap.add_argument("--json", action="store_true", help="JSONで出力(他のAIへ渡す用)")
    args = ap.parse_args()
    if args.day is None:
        args.day = dp.current_day()

    slots = [args.time] if args.time else dp.SLOTS
    if args.time and args.time not in dp.SLOTS:
        print(f"時間帯は {'/'.join(dp.SLOTS)} のいずれか", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(brief(args.day, slots), ensure_ascii=False, indent=1))
        return 0

    rows = dp.load_rows()
    by_name = {r["名前"]: r for r in rows}
    cal = dp.calendar_of(args.day)
    print("=" * 60)
    print(f"クロスロード {args.day}日目  {cal['表記']}／空模様:{dp.weather_of(args.day)}")
    for ev in dp.festivals_of(args.day):
        print(f"◎ 本日:{ev}")
    print("=" * 60)
    for slot in slots:
        print("\n" + dp.render_slot(rows, by_name, args.day, slot))
    print("\n" + qb.render(args.day))
    print("\n" + st.render(args.day))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
