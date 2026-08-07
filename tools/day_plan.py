#!/usr/bin/env python3
"""日付と時間帯から「今どこに誰がいるか」を機械的に決めるツール(街の配置生成)。

各人の生活ルーティン(`tools/routines.tsv`)に重み付き乱数を掛けて、その日その刻の
居場所を確定させる。GMが「誰をどこに出すか」を都合で選ぶのではなく、街の側が
勝手に動いている状態を先に作り、GMはその配置を見てから場面を選ぶ。

同じ日付・時間帯なら何度実行しても同じ配置が出る(日付を種にした固定乱数)。

住人は行動型で分かれる。不動(持ち場を離れない店主・門衛・受付など)は毎日そこにいる。
定住は拠点を持ちつつ時々ふらつく。遊動(衛兵隊長・連絡役・情報屋・潜入・盗人など)は
一日中街をうろつくため、その刻に回る先も併せて出る。

粒度は区画レベル(5区画+下水道+危険地域4+ダンジョン3+街道4)。
その区画の中のどの店・施設かは`tools/scene_context.py`と`world/crossroad/72_place_character_map.md`で詰める。

使い方:
    python3 tools/day_plan.py --day 3 --time 宵      # その刻の街全体の配置
    python3 tools/day_plan.py --day 3                # 一日ぶん(6時間帯)を通しで
    python3 tools/day_plan.py --day 3 --place 東区   # 特定の場所だけ
    python3 tools/day_plan.py --day 3 --who ミルカ   # 一人の一日を追う
"""
from __future__ import annotations
import argparse
import hashlib
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTINE_FILE = os.path.join(ROOT, "tools", "routines.tsv")

SLOTS = ["未明", "朝", "昼", "夕", "宵", "夜半"]
AWAY_SLOTS = ["朝", "昼", "夕"]  # 遠出は日帰り想定。宵には街に戻る

IN_TOWN = ["中央区", "北区", "東区", "南区", "西区", "下水道"]
DANGER = ["さざめき平原", "赤牙森林", "灰岩峡谷", "骨鳴り墓原"]
DUNGEON = ["黒硝子遺跡", "忘れられた鉱山", "星喰いの地下神殿"]
ROADS = ["王都街道", "麦穂街道", "森境街道", "灰岩街道"]
KNOWN = IN_TOWN + DANGER + DUNGEON + ROADS

COLUMNS = ["名前", "ファイル", "行動型", "同行", "追従", "遠出率", "遠出先", "既定"] + SLOTS


def rng(*parts) -> random.Random:
    """入力から決まる固定乱数(実行のたびに変わらない)。"""
    key = "|".join(str(p) for p in parts)
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]
    return random.Random(int(digest, 16))


def parse_weights(cell: str) -> list[tuple[str, float]]:
    out = []
    for item in cell.split("|"):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            name, _, w = item.partition(":")
            out.append((name.strip(), float(w)))
        else:
            out.append((item, 1.0))
    return out


def pick(weights: list[tuple[str, float]], r: random.Random) -> str:
    total = sum(w for _, w in weights)
    x = r.random() * total
    for name, w in weights:
        x -= w
        if x < 0:
            return name
    return weights[-1][0]


def load_rows() -> list[dict]:
    rows = []
    with open(ROUTINE_FILE, encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            cells = line.split("\t")
            if header is None:
                header = cells
                continue
            row = {h: (cells[i].strip() if i < len(cells) else "") for i, h in enumerate(header)}
            rows.append(row)
    return rows


def validate(rows: list[dict]) -> list[str]:
    problems = []
    names = {r["名前"] for r in rows}
    for r in rows:
        if r["同行"] and r["同行"] not in names:
            problems.append(f"{r['名前']}:同行先「{r['同行']}」が表にない")
        if r.get("追従") and parse_follow(r["追従"])[0] not in names:
            problems.append(f"{r['名前']}:追従先「{r['追従']}」が表にない")
        for col in ["遠出先", "既定"] + SLOTS:
            for loc, _ in parse_weights(r.get(col, "")):
                if loc not in KNOWN:
                    problems.append(f"{r['名前']}/{col}:未知の場所「{loc}」")
        mv = r.get("行動型") or "定住"
        if mv not in ("不動", "定住", "遊動"):
            problems.append(f"{r['名前']}:行動型「{mv}」は不動/定住/遊動のいずれか")
        if not r["既定"]:
            problems.append(f"{r['名前']}:既定の居場所が空")
    return problems


def leader_of(row: dict, by_name: dict[str, dict]) -> dict:
    seen = {row["名前"]}
    cur = row
    while cur["同行"] and cur["同行"] in by_name and cur["同行"] not in seen:
        seen.add(cur["同行"])
        cur = by_name[cur["同行"]]
    return cur


def away_today(row: dict, day: int, by_name: dict[str, dict]) -> str | None:
    """その日、市外へ出ているなら行き先を返す。"""
    lead = leader_of(row, by_name)
    rate = float(lead["遠出率"] or 0)
    dests = parse_weights(lead["遠出先"])
    if rate <= 0 or not dests:
        return None
    r = rng("away", day, lead["名前"])
    if r.random() * 100 >= rate:
        return None
    return pick(dests, rng("dest", day, lead["名前"]))


def slot_weights(row: dict, slot: str) -> list[tuple[str, float]]:
    return parse_weights(row.get(slot, "")) or parse_weights(row["既定"])


def move_type(row: dict) -> str:
    return row.get("行動型") or "定住"


def is_unusual(row: dict, slot: str, place: str) -> bool:
    """その人にしては珍しい場所か(いつもの場所の半分未満の重みなら珍しい扱い)。

    持ち場を動かない者(不動)と、元から街中を巡る者(遊動)には珍しいも何もないので付けない。
    """
    if move_type(row) != "定住":
        return False
    weights = dict(slot_weights(row, slot))
    top = max(weights.values())
    return weights.get(place, 0) < top / 2


def route_of(row: dict, day: int, slot: str, place: str) -> str:
    """遊動型が、その刻のうちに合わせて回る先(なければ空)。"""
    if move_type(row) != "遊動" or place not in IN_TOWN:
        return ""
    rest = [(p, w) for p, w in slot_weights(row, slot) if p != place]
    if not rest:
        return ""
    return pick(rest, rng("route", day, slot, row["名前"]))


def parse_follow(cell: str) -> tuple[str, float]:
    name, _, prob = cell.partition(":")
    return name.strip(), (float(prob) if prob.strip() else 100.0)


def locate(row: dict, day: int, slot: str, by_name: dict[str, dict],
           depth: int = 0) -> tuple[str, str]:
    """(場所, 注記)を返す。"""
    dest = away_today(row, day, by_name)
    if dest and slot in AWAY_SLOTS:
        lead = leader_of(row, by_name)
        note = "" if lead["名前"] == row["名前"] else f"{lead['名前']}に同行"
        return dest, note

    # 供として付いて回る者は、その確率で相手と同じ区画に出る
    follow = row.get("追従", "")
    if follow and depth < 3:
        target, prob = parse_follow(follow)
        if target in by_name and rng("follow", day, slot, row["名前"]).random() * 100 < prob:
            place, _ = locate(by_name[target], day, slot, by_name, depth + 1)
            if place in IN_TOWN:  # 相手が市外にいる時は置いていかれる(自分の重みで動く)
                return place, f"{target}の供"

    weights = slot_weights(row, slot)
    if move_type(row) == "不動":  # 持ち場から動かない者は毎日そこにいる
        return max(weights, key=lambda x: x[1])[0], ""
    place = pick(weights, rng("place", day, slot, row["名前"]))
    return place, ("いつもと違う" if is_unusual(row, slot, place) else "")


def render_slot(rows: list[dict], by_name: dict[str, dict], day: int, slot: str,
                place_filter: str = "") -> str:
    placed: dict[str, list[str]] = {}
    passing: dict[str, list[str]] = {}  # 遊動型が巡回で通りかかる先
    for row in rows:
        place, note = locate(row, day, slot, by_name)
        label = row["名前"]
        if note == "いつもと違う":
            label = "※" + label
        elif note:
            label = f"{label}({note})"
        route = route_of(row, day, slot, place)
        placed.setdefault(place, []).append(label + (f"→{route}" if route else ""))
        if route:
            passing.setdefault(route, []).append(row["名前"])

    order = [p for p in KNOWN if p in placed]
    lines = [f"── {day}日目・{slot} ──"]
    town, outside = [], []
    for place in order:
        entry = f"■ {place}({len(placed[place])}人)\n   " + "／".join(placed[place])
        if place in passing:
            entry += "\n   (巡回で通りかかる:" + "／".join(passing[place]) + ")"
        (town if place in IN_TOWN else outside).append(entry)
    if place_filter:
        hits = [e for e in town + outside if e.startswith(f"■ {place_filter}")]
        if not hits and place_filter in passing:
            hits = [f"■ {place_filter}(0人)\n   (巡回で通りかかる:"
                    + "／".join(passing[place_filter]) + ")"]
        lines += hits or [f"(この刻、{place_filter}には誰もいない)"]
        return "\n".join(lines)
    lines += town
    if outside:
        lines.append("【市外】")
        lines += outside
    return "\n".join(lines)


def render_who(rows: list[dict], by_name: dict[str, dict], day: int, who: str) -> str:
    hits = [r for r in rows if who in r["名前"]]
    if not hits:
        return f"(「{who}」は routines.tsv に見つからない)"
    out = []
    for row in hits:
        lines = [f"── {row['名前']}の{day}日目 ──"]
        lines[0] += f"({move_type(row)}型)"
        for slot in SLOTS:
            place, note = locate(row, day, slot, by_name)
            route = route_of(row, day, slot, place)
            suffix = f"→{route}" if route else ""
            suffix += f"  ({note})" if note else ""
            lines.append(f"  {slot:<4}… {place}{suffix}")
        out.append("\n".join(lines))
    return "\n\n".join(out)


FOOTER = """【この配置の使い方】
- ここで決まった居場所は、GMの都合ではなく街のルーティン+乱数の結果。※印は「その人にしては珍しい場所」で、
  場面の種として使いやすい(なぜ今日はそこにいるのか、はGMが自由に決めてよい)。
- 住人は行動型で分かれる。**不動**(店主・門衛・受付・病院・下水道など持ち場を離れない者)は毎日そこにいるので、
  その区画へ行けば必ず会える。**定住**は拠点はあるが時々ふらつく。**遊動**(衛兵隊長・連絡役・情報屋・潜入・
  盗人・取材屋など)は一日中うろつくため、`→区画`で「その刻のうちに回る先」も出る——どちらの区画で出しても矛盾しない。
- 区画の中のどの店・施設かは `world/crossroad/72_place_character_map.md`・`world/crossroad/49_crossroad_dining.md` で決める。
- 場面に出す人物が決まったら `python3 tools/scene_context.py --chars ... --place ... --time ...` で
  ステータス・スキル・口調を引いてから描写する。
- 遠出は日帰り想定(朝〜夕が市外)。泊まりがけにしたい時は翌日も同じ行き先に据え置いてよい。"""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", type=int, default=1, help="作中の日付(同じ数字なら同じ配置)")
    ap.add_argument("--time", default="", help=f"時間帯({'/'.join(SLOTS)})。省略で一日ぶん")
    ap.add_argument("--place", default="", help="この場所だけ表示")
    ap.add_argument("--who", default="", help="この人物の一日を追う")
    ap.add_argument("--check", action="store_true", help="ルーティン表の整合だけ確認する")
    args = ap.parse_args()

    rows = load_rows()
    by_name = {r["名前"]: r for r in rows}

    problems = validate(rows)
    if args.check:
        if problems:
            print("\n".join(problems))
            return 1
        print(f"routines.tsv:{len(rows)}件、問題なし")
        return 0
    if problems:
        print("(ルーティン表に問題あり)\n" + "\n".join(problems), file=sys.stderr)

    if args.time and args.time not in SLOTS:
        print(f"時間帯は {'/'.join(SLOTS)} のいずれか", file=sys.stderr)
        return 1

    blocks = ["=" * 60,
              f"クロスロードの街の様子({args.day}日目) 機械生成:ルーティン表+固定乱数",
              "=" * 60]
    if args.who:
        blocks.append(render_who(rows, by_name, args.day, args.who))
    else:
        slots = [args.time] if args.time else SLOTS
        for slot in slots:
            blocks.append(render_slot(rows, by_name, args.day, slot, args.place))
    blocks.append(FOOTER)
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
