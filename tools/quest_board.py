#!/usr/bin/env python3
"""その日の掲示板を組み立てるツール(冒険者ギルドの依頼板／区画ごとの街区掲示板)。

依頼はその場で考えず、既存の依頼表(`world/crossroad/64・65・66`)の掲示例から
日付固定の乱数で選ぶ。報酬額も表の値をそのまま使うので、`world/06_economy.md`の
相場から外れた金額が即興で出てくることがない。

未受注の依頼は数日そのまま貼られ続ける(継続掲示)。また、その日に実際どこへ
誰が出ているか(`tools/day_plan.py`)を突き合わせ、現地に出ている顔ぶれも併記する。

使い方:
    python3 tools/quest_board.py --day 8           # その日の掲示板
    python3 tools/quest_board.py --day 8 --rank D  # ランクで絞る
    python3 tools/quest_board.py --day 8 --all     # 掲示例の全件(表の元データ)
    python3 tools/quest_board.py --day 8 --district 東区  # 区画の街区掲示板(軽い仕事・告知)
"""
from __future__ import annotations
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import day_plan as dp  # noqa: E402

ROOT = dp.ROOT
QUEST_FILES = [
    ("危険地域", os.path.join(ROOT, "world", "crossroad", "64_danger_zone_quest_board.md")),
    ("ダンジョン", os.path.join(ROOT, "world", "crossroad", "65_dungeon_quest_board.md")),
    ("護衛・治安", os.path.join(ROOT, "world", "crossroad", "66_civilian_security_quest_board.md")),
]
RANKS = ["F", "E", "D", "C", "B", "A", "S"]

# 街区掲示板(ギルドの正式依頼板とは別。区画ごとの軽い仕事・告知・怪しい張り紙)
DISTRICT_BOARD = os.path.join(ROOT, "world", "crossroad", "22_crossroad_bulletin_boards.md")
DISTRICT_NEW = (2, 4)      # 一日に貼り替わる枚数
DISTRICT_LIFE = (2, 6)     # 貼られたままになる日数
SHADY_CHANCE = 25          # 怪しい張り紙が混じる確率(%)

# 一日に新しく貼り出される件数と、貼られたままになる日数
NEW_PER_DAY = (3, 6)
POST_LIFE = (2, 5)

# 掲示の偏りを防ぐ重み。討伐の大半は日常的な間引き・素材調達(CLAUDE.md)なので、
# 危険地域の採取・討伐を厚く、ダンジョンは細く出す。
SOURCE_WEIGHT = {"危険地域": 5, "護衛・治安": 4, "ダンジョン": 2}

# クロスロードは中級者向けの街で、Lv50を大きく超える稼ぎ場が乏しい
# (`world/crossroad/11_crossroad_city.md`)。高ランク依頼はめったに貼られない。
RANK_WEIGHT = {"F": 3, "E": 5, "D": 5, "C": 4, "B": 1.5, "A": 0.6, "S": 0.2}


def load_quests() -> list[dict]:
    quests = []
    for source, path in QUEST_FILES:
        section = ""
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.startswith("## "):
                section = re.sub(r"^[①-⑳\s]+", "", line[3:]).strip()
                continue
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 5 or cells[1] not in RANKS:
                continue
            quests.append({
                "名": cells[0], "ランク": cells[1], "内容": cells[2],
                "人数": cells[3], "報酬": cells[4],
                "舞台": section, "出所": source, "出典": os.path.basename(path),
            })
    return quests


def load_district_notices() -> dict[str, list[dict]]:
    """22の掲示例を区画ごとに読む(怪しい張り紙は「怪しい張り紙」キー)。"""
    out: dict[str, list[dict]] = {}
    section = ""
    for line in open(DISTRICT_BOARD, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("### "):
            head = line[4:]
            section = "怪しい張り紙" if "怪しい" in head else head.replace("の掲示例", "").strip()
            continue
        if not section or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 4 and cells[0] not in ("掲示",) and not set(cells[0]) <= set("-: "):
            out.setdefault(section, []).append(
                {"掲示": cells[0], "出す人": cells[1], "内容": cells[2], "報酬": cells[3]})
        elif len(cells) == 3 and cells[0] != "掲示" and not set(cells[0]) <= set("-: "):
            out.setdefault(section, []).append(
                {"掲示": cells[0], "出す人": "(素性不明)", "内容": cells[1], "報酬": cells[2]})
    return out


def district_board(day: int, district: str) -> list[dict]:
    """その日、その区画の街区掲示板に貼られているもの。"""
    notices = load_district_notices()
    pool = notices.get(district, [])
    shady = notices.get("怪しい張り紙", [])
    if not pool:
        return []
    board, seen = [], set()
    for start in range(max(1, day - max(DISTRICT_LIFE) + 1), day + 1):
        n = dp.rng("dboard", start, district).randint(*DISTRICT_NEW)
        for k in range(n):
            r = dp.rng("dpick", start, district, k)
            # 西区・北区の端には、正規の掲示に紛れて素性の知れない張り紙が出る
            src = shady if (district in ("西区", "北区") and shady
                            and r.random() * 100 < SHADY_CHANCE) else pool
            item = src[r.randrange(len(src))]
            life = dp.rng("dlife", start, district, k).randint(*DISTRICT_LIFE)
            if start + life <= day or item["掲示"] in seen:
                continue  # 期限切れの分は、後日また貼り出されてよい
            seen.add(item["掲示"])
            board.append(dict(item, 経過=day - start, 怪しい=(src is shady)))
    return board


def render_district(day: int, district: str) -> str:
    board = district_board(day, district)
    cal = dp.calendar_of(day)
    out = ["=" * 60,
           f"{district} 街区掲示板({day}日目)  {cal['表記']}／空模様:{dp.weather_of(day)}",
           "=" * 60]
    if not board:
        return "\n".join(out + [f"(区画名は 中央区/北区/東区/南区/西区 のいずれか)"])
    for q in sorted(board, key=lambda x: x["経過"]):
        mark = "※怪しい張り紙 " if q["怪しい"] else ""
        age = "本日貼り出し" if q["経過"] == 0 else f"貼り出し{q['経過'] + 1}日目"
        out.append(f"- {mark}{q['掲示']}　[{q['出す人']}／{q['報酬']}／{age}]\n    {q['内容']}")
    out.append("""
【使い方】
- ギルドの正式依頼板(`tools/quest_board.py --day N`)とは別物。ランクも安全確認もない軽い仕事・告知が中心で、
  報酬は日常価格帯(`world/06_economy.md`)に収まる。出典は`world/crossroad/22_crossroad_bulletin_boards.md`。
- **掲示板は冒険者と住民が接触する動線**。出す人が既存NPCなら、その人物のところへ行けば直接受けられる。
  依頼そのものより「そこで誰と知り合うか」が本体である場合も多い。
- 怪しい張り紙は、出したからといって毎回裏がある必要はない(実際は割の良いだけの仕事、も普通にある)。""")
    return "\n".join(out)


def stage_place(quest: dict) -> str:
    """依頼の舞台を、day_plan.pyの場所語彙に対応づける(該当なしは空)。"""
    for place in dp.KNOWN:
        if place in quest["舞台"] or place in quest["内容"] or place in quest["名"]:
            return place
    return ""


def festival_near(day: int, span: int = 4) -> bool:
    return any(dp.festivals_of(d) for d in range(day, day + span))


def posted_on(day: int, quests: list[dict]) -> list[dict]:
    """その日に新しく貼り出される依頼。"""
    n = dp.rng("board", day).randint(*NEW_PER_DAY)
    weights = []
    for i, q in enumerate(quests):
        # 祭りの警備依頼は、祭りが近い日にだけ貼り出す
        if re.search(r"祭り|祭礼|大型イベント", q["名"] + q["内容"]) and not festival_near(day):
            continue
        weights.append((str(i), SOURCE_WEIGHT.get(q["出所"], 1) * RANK_WEIGHT[q["ランク"]]))
    out, used = [], set()
    for k in range(n * 4):
        if len(out) >= n:
            break
        idx = int(dp.pick(weights, dp.rng("pickq", day, k)))
        if idx in used:
            continue
        used.add(idx)
        q = dict(quests[idx])
        q["掲示日"] = day
        q["掲示期間"] = dp.rng("life", day, idx).randint(*POST_LIFE)
        out.append(q)
    return out


def board_of(day: int, quests: list[dict]) -> list[dict]:
    """その日に貼られている依頼(新規＋まだ残っている継続分)。同じ依頼は重ねて貼らない。"""
    board, seen = [], set()
    for start in range(max(1, day - max(POST_LIFE) + 1), day + 1):
        for q in posted_on(start, quests):
            if q["名"] in seen:
                continue  # 先に貼られている分を優先
            seen.add(q["名"])
            if start + q["掲示期間"] > day:
                q["経過"] = day - start
                board.append(q)
    return board


def render(day: int, rank: str = "") -> str:
    quests = load_quests()
    board = board_of(day, quests)
    if rank:
        board = [q for q in board if q["ランク"] == rank.upper()]

    rows = dp.load_rows()
    by_name = {r["名前"]: r for r in rows}
    at_place: dict[str, list[str]] = {}
    for row in rows:
        place, _ = dp.locate(row, day, "昼", by_name)
        if place not in dp.IN_TOWN:
            at_place.setdefault(place, []).append(row["名前"])

    cal = dp.calendar_of(day)
    out = ["=" * 60,
           f"冒険者ギルド クロスロード支部 掲示板({day}日目)  {cal['表記']}／空模様:{dp.weather_of(day)}",
           "=" * 60]
    for ev in dp.festivals_of(day):
        out.append(f"◎ 本日:{ev}")

    new = [q for q in board if q["経過"] == 0]
    old = sorted((q for q in board if q["経過"] > 0), key=lambda q: q["経過"])
    for title, group in [("本日の新規掲示", new), ("継続掲示(まだ受け手がついていない)", old)]:
        if not group:
            continue
        out.append(f"\n【{title}】")
        for q in group:
            place = stage_place(q)
            head = f"[{q['ランク']}] {q['名']}"
            meta = f"{q['舞台']}／{q['人数']}／{q['報酬']}"
            if q["経過"]:
                meta += f"／掲示{q['経過'] + 1}日目"
            out.append(f"- {head}\n    {meta}\n    {q['内容']}")
            if place and place in at_place:
                out.append(f"    ※現地には今日 {'・'.join(at_place[place])} が出ている")

    if at_place:
        out.append("\n【今日、街の外に出ている顔ぶれ】")
        for place, who in at_place.items():
            out.append(f"- {place}:{'・'.join(who)}")

    out.append("""
【使い方】
- ここに出た依頼は`world/crossroad/64・65・66`の掲示例そのままで、報酬額も`world/06_economy.md`の
  相場に沿った表の値。金額を場の勢いで決めないための土台として使う(報酬は1人あたりの目安)。
- 討伐依頼の大半は特別な背景を持たない日常的な間引き・素材調達(`world/14_adventurers_guild.md`)。
  裏の陰謀を毎回挟まない。大きな案件をやる時は`world/crossroad/75_scenario_seeds.md`から持ってくる。
- 表にない舞台(名もない村・森・洞窟)で依頼を作りたい時は、`world/07・08・09`の生成ルールに沿って
  その場で新しい舞台を起こしてよい。""")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", type=int, default=None, help="作中の日付")
    ap.add_argument("--rank", default="", help="このランクだけ表示(F〜S)")
    ap.add_argument("--district", default="", help="街区掲示板を出す(中央区/北区/東区/南区/西区)")
    ap.add_argument("--all", action="store_true", help="掲示例の全件を出す(表の元データ確認用)")
    args = ap.parse_args()
    if args.day is None:
        args.day = dp.current_day()

    if args.all:
        for q in load_quests():
            print(f"[{q['ランク']}] {q['名']}\t{q['舞台']}\t{q['報酬']}\t({q['出典']})")
        return 0
    if args.district:
        print(render_district(args.day, args.district))
        return 0
    print(render(args.day, args.rank))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
