#!/usr/bin/env python3
"""日付と時間帯から「今どこに誰がいるか」を機械的に決めるツール(街の配置生成)。

各人の生活ルーティン(`tools/routines.tsv`)に重み付き乱数を掛けて、その日その刻の
居場所を確定させる。GMが「誰をどこに出すか」を都合で選ぶのではなく、街の側が
勝手に動いている状態を先に作り、GMはその配置を見てから場面を選ぶ。

日付からは暦(1年12ヶ月×30日×三旬)・年中行事・空模様も同時に決まる(`world/70_calendar_and_climate.md`)。
同じ日付・時間帯なら何度実行しても同じ配置・同じ天候が出る(日付を種にした固定乱数)。

住人は行動型で分かれる。不動(持ち場を離れない店主・門衛・受付など)は毎日そこにいる。
定住は拠点を持ちつつ時々ふらつく。遊動(衛兵隊長・連絡役・情報屋・潜入・盗人など)は
一日中街をうろつくため、その刻に回る先も併せて出る。

場所は区画(5区画+下水道+危険地域4+ダンジョン3+街道4)で決まり、市内はさらに区画の中の
店・施設まで割り振る(`world/crossroad/72_place_character_map.md`の施設常駐と行きつけ・宿から
`tools/venue_map.py`が抽出。店の種別と時間帯が噛み合う所へ入る)。

使い方:
    python3 tools/day_plan.py --day 3 --time 宵      # その刻の街全体の配置
    python3 tools/day_plan.py --day 3                # 一日ぶん(6時間帯)を通しで
    python3 tools/day_plan.py --day 3 --place 東区   # 特定の場所だけ
    python3 tools/day_plan.py --day 3 --who ミルカ   # 一人の一日を追う
    python3 tools/day_plan.py --check                # ルーティン表の整合確認
"""
from __future__ import annotations
import argparse
import hashlib
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTINE_FILE = os.path.join(ROOT, "tools", "routines.tsv")
DAY_FILE = os.path.join(ROOT, "tools", "session_day.txt")

SLOTS = ["未明", "朝", "昼", "夕", "宵", "夜半"]
AWAY_SLOTS = ["朝", "昼", "夕"]  # 遠出は日帰り想定。宵には街に戻る

IN_TOWN = ["中央区", "北区", "東区", "南区", "西区", "下水道"]
DANGER = ["さざめき平原", "赤牙森林", "灰岩峡谷", "骨鳴り墓原"]
DUNGEON = ["黒硝子遺跡", "忘れられた鉱山", "星喰いの地下神殿"]
ROADS = ["王都街道", "麦穂街道", "森境街道", "灰岩街道"]
KNOWN = IN_TOWN + DANGER + DUNGEON + ROADS

COLUMNS = ["名前", "ファイル", "行動型", "同行", "追従", "遠出率", "遠出先", "既定"] + SLOTS

NPC_DIR = os.path.join(ROOT, "characters", "npcs")

# 遠出の泊まり数(`world/crossroad/11_crossroad_city.md`の距離感。ダンジョンは泊まりがけ)
TRIP_DAYS = {
    "黒硝子遺跡": (2, 3), "忘れられた鉱山": (2, 3), "星喰いの地下神殿": (3, 4),
    "骨鳴り墓原": (1, 2), "灰岩峡谷": (1, 2), "赤牙森林": (1, 1), "さざめき平原": (1, 1),
    "王都街道": (2, 3), "麦穂街道": (1, 1), "森境街道": (1, 2), "灰岩街道": (2, 2),
}
MAX_TRIP = 4

# 暦(`world/70_calendar_and_climate.md`):1年12ヶ月×30日×三旬
MONTH_NAMES = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
WEATHER = [(3, "晴れ／薄曇り"), (4, "曇り"), (5, "小雨〜雨"), (6, "荒天")]


def current_day() -> int:
    """今が作中の何日目か(`tools/session_day.txt`)。日付を省略した時に使う。"""
    try:
        return int(open(DAY_FILE, encoding="utf-8").read().strip())
    except (OSError, ValueError):
        return 1


def set_day(day: int) -> None:
    with open(DAY_FILE, "w", encoding="utf-8") as f:
        f.write(f"{day}\n")


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


def trip_started(lead: dict, day: int) -> tuple[str, int] | None:
    """その日に市外へ発つなら(行き先, 泊まりを含む日数)を返す。"""
    rate = float(lead["遠出率"] or 0)
    dests = parse_weights(lead["遠出先"])
    if rate <= 0 or not dests:
        return None
    # 天候の影響(world/70):荒天は門の出入りが制限され商隊も足止め、雨も出足が鈍る
    sky = weather_of(day)
    if sky == "荒天":
        rate *= 0.25
    elif sky == "小雨〜雨":
        rate *= 0.85
    if rng("away", day, lead["名前"]).random() * 100 >= rate:
        return None
    dest = pick(dests, rng("dest", day, lead["名前"]))
    lo, hi = TRIP_DAYS.get(dest, (1, 1))
    return dest, rng("triplen", day, lead["名前"]).randint(lo, hi)


def away_today(row: dict, day: int, by_name: dict[str, dict]) -> tuple[str, bool, bool] | None:
    """その日、市外にいるなら(行き先, 出発日か, 帰還日か)を返す(泊まりがけを含む)。"""
    lead = leader_of(row, by_name)
    for start in range(max(1, day - MAX_TRIP + 1), day + 1):
        trip = trip_started(lead, start)
        if trip and start <= day < start + trip[1]:  # 先に始まった旅程が優先
            return trip[0], day == start, day == start + trip[1] - 1
    return None


def away_at(slot: str, first: bool, last: bool) -> bool:
    """その時間帯に市外にいるか。出発日は朝発ち、帰還日は宵に街へ戻る。"""
    if first and last:
        return slot in AWAY_SLOTS          # 日帰り:朝〜夕
    if first:
        return slot != "未明"               # 出発日:朝発ち、その晩は野営や宿
    if last:
        return slot in ["未明"] + AWAY_SLOTS  # 帰還日:宵に街へ戻る
    return True                             # 道中の日は終日


def calendar_of(day: int) -> dict:
    """通し日数から暦(年・月・旬・日)を出す。1日目=一年目 一の月 上旬 1日。"""
    idx = day - 1
    year, rest = idx // 360 + 1, idx % 360
    month, dom = rest // 30 + 1, rest % 30 + 1
    jun = "上旬" if dom <= 10 else ("中旬" if dom <= 20 else "下旬")
    return {"年": year, "月": month, "日": dom, "旬": jun,
            "表記": f"{year}年 {MONTH_NAMES[month - 1]}の月 {jun}{dom}日"}


def weather_of(day: int) -> str:
    """その日の空模様(world/70の1d6表)。

    毎日を機械生成すると1/6では荒天が多すぎる(canonは「荒天は稀」)ため、
    6が出た時だけもう一度振り、6でのみ荒天とする(1/36≒年に10日)。
    """
    r = rng("weather", day)
    roll = r.randint(1, 6)
    if roll == 6 and r.randint(1, 6) < 6:
        return "曇り"
    for limit, name in WEATHER:
        if roll <= limit:
            return name
    return WEATHER[-1][1]


def festivals_of(day: int) -> list[str]:
    """その日の年中行事(world/70「年中行事の位置づけ」)。"""
    cal = calendar_of(day)
    out = []
    # 巡穣祭:月に一度・一日。開催日は収穫状況を見て決まる(47)ので月ごとに揺れる
    fest_day = rng("harvest", cal["年"], cal["月"]).randint(18, 28)
    if cal["日"] == fest_day:
        out.append("巡穣祭(月に一度の食の祭り。街全体が一つの食材に染まる。"
                   "`world/crossroad/47_crossroad_harvest_festival.md`)")
    # 結び路の祝祭:年に一度・七日間(五の月 中旬11〜17日)。中央区が祭り区域
    if cal["月"] == 5 and 11 <= cal["日"] <= 17:
        out.append(f"結び路の祝祭 {cal['日'] - 10}日目/7日間(婚活祭り。中央大広場一帯。"
                   "`world/crossroad/46_crossroad_matchmaking_festival.md`)")
    # 年次追加改修祭:年に一度、南区の職人が一斉にアイアンくんを改修(十の月 中旬15日)
    if cal["月"] == 10 and cal["日"] == 15:
        out.append("年次追加改修祭(南区の職人が一斉にアイアンくんを改修。"
                   "`characters/npcs/30_ultimate_patchwork_iron_kun.md`)")
    return out


def festival_place(day: int) -> tuple[str, str] | None:
    """祭りが人を集めている区画と、その注記。"""
    cal = calendar_of(day)
    if cal["月"] == 5 and 11 <= cal["日"] <= 17:
        return "中央区", "結び路の祝祭"      # 中央大広場一帯が祭り区域(46)
    if cal["月"] == 10 and cal["日"] == 15:
        return "南区", "年次追加改修祭"       # 南区中央広場のアイアンくん(30)
    if cal["日"] == rng("harvest", cal["年"], cal["月"]).randint(18, 28):
        return "中央区", "巡穣祭"            # 中央広場の朝市を中心に街全体(47)
    return None


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
    trip = away_today(row, day, by_name)
    if trip and away_at(slot, trip[1], trip[2]):
        lead = leader_of(row, by_name)
        note = "" if lead["名前"] == row["名前"] else f"{lead['名前']}に同行"
        if not trip[1]:  # 出発日でない=泊まりがけの途中
            note = (note + "・" if note else "") + ("帰路" if trip[2] else "泊まり")
        return trip[0], note

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

    # 祭りの日は、そこへ足を運ぶ者が出る(持ち場を離れない不動型は動かない)
    fest = festival_place(day)
    if fest and slot in ("昼", "夕", "宵") and \
            rng("fest", day, slot, row["名前"]).random() < 0.45:
        return fest[0], fest[1]
    place = pick(weights, rng("place", day, slot, row["名前"]))
    return place, ("いつもと違う" if is_unusual(row, slot, place) else "")


def relations(rows: list[dict]) -> dict[str, set[str]]:
    """各`characters/npcs/`の「よく接する人物」から知人関係を作る(ファイル番号で照合)。"""
    import re
    by_num = {r["ファイル"]: r["名前"] for r in rows}
    graph: dict[str, set[str]] = {r["名前"]: set() for r in rows}
    for row in rows:
        path = None
        for fn in os.listdir(NPC_DIR):
            if fn.startswith(row["ファイル"] + "_"):
                path = os.path.join(NPC_DIR, fn)
                break
        if not path:
            continue
        text = open(path, encoding="utf-8").read()
        # 「よく接する人物」だけでなく「◯◯との関係」「相互関係」も拾う。
        # 災害パーティーのように、仲間の話を専用節に書いているファイルがあるため
        chunks = [m.group(1) for m in re.finditer(
            r"(?m)^## (?:よく接する人物|[^\n]*関係)\n(.*?)(?=\n## |\Z)", text, re.S)]
        if not chunks:
            continue
        for num in re.findall(r"characters/npcs/(\d+)_", "\n".join(chunks)):
            other = by_num.get(num)
            if other and other != row["名前"]:
                graph[row["名前"]].add(other)
                graph[other].add(row["名前"])
    return graph


def render_encounters(rows: list[dict], by_name: dict[str, dict], day: int, slot: str,
                      located: dict[str, tuple[str, str]]) -> str:
    """今日のめぐり合わせ(市外での鉢合わせ・珍しい場所での顔合わせ)を拾う。"""
    graph = relations(rows)
    lines = []

    # 市外で別々のグループが同じ場所に居合わせている
    outside: dict[str, list[dict]] = {}
    for row in rows:
        place, _ = located[row["名前"]]
        if place not in IN_TOWN:
            outside.setdefault(place, []).append(row)
    for place, members in outside.items():
        groups = {}
        for row in members:
            groups.setdefault(leader_of(row, by_name)["名前"], []).append(row["名前"])
        if len(groups) > 1:
            desc = "／".join("・".join(g) for g in groups.values())
            lines.append(f"- {place}に{len(groups)}組が居合わせている:{desc}")

    # いつもと違う区画にいる者が、そこで知人と鉢合わせている(同じ組み合わせは一度だけ)
    seen: set[frozenset] = set()
    for row in rows:
        place, note = located[row["名前"]]
        if note != "いつもと違う":
            continue
        here = []
        for other in sorted(graph[row["名前"]]):
            if located[other][0] != place or frozenset((row["名前"], other)) in seen:
                continue
            seen.add(frozenset((row["名前"], other)))
            here.append(other)
        if here:
            lines.append(f"- ※{row['名前']}が{place}にいて、{'・'.join(here)}と同じ区画")

    if not lines:
        return ""
    return "【今日のめぐり合わせ】\n" + "\n".join(lines)


_VENUES: dict[str, list[dict]] | None = None


def venue_table(rows: list[dict]) -> dict[str, list[dict]]:
    global _VENUES
    if _VENUES is None:
        import venue_map
        _VENUES = venue_map.load(rows)
    return _VENUES


def render_venues(place: str, slot: str, day: int, labels: list[str],
                  by_name: dict[str, dict]) -> str:
    """区画の中を、店・施設ごとに割り振って書き出す(市外や該当なしはそのまま)。"""
    import venue_map
    if place not in IN_TOWN:
        return "   " + "／".join(labels)
    venues = venue_table(list(by_name.values()))
    groups: dict[str, list[str]] = {}
    loose: list[str] = []
    for label in labels:
        person = re.sub(r"^※|[(→].*", "", label)
        row = by_name.get(person)
        slack = 1.0 if row and move_type(row) == "不動" else 3.0
        spot = venue_map.pick_venue(person, place, slot, venues,
                                    rng("venue", day, slot, person), slack)
        (groups.setdefault(spot, []) if spot else loose).append(label)
    out = [f"   《{v}》" + "／".join(who) for v, who in groups.items()]
    if loose:
        out.append("   (区画内)" + "／".join(loose))
    return "\n".join(out)


def render_slot(rows: list[dict], by_name: dict[str, dict], day: int, slot: str,
                place_filter: str = "") -> str:
    placed: dict[str, list[str]] = {}
    passing: dict[str, list[str]] = {}  # 遊動型が巡回で通りかかる先
    located: dict[str, tuple[str, str]] = {}
    for row in rows:
        place, note = locate(row, day, slot, by_name)
        located[row["名前"]] = (place, note)
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
        entry = f"■ {place}({len(placed[place])}人)\n" + render_venues(
            place, slot, day, placed[place], by_name)
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
    meets = render_encounters(rows, by_name, day, slot, located)
    if meets:
        lines += ["", meets]
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
- 遠出は行き先の遠さで日数が決まる。近場(さざめき平原・赤牙森林)は日帰り、ダンジョンや王都街道は泊まりがけで、
  `泊まり`は道中の日、`帰路`は宵に街へ戻る日。荒天の日は門が制限され、新たに発つ者が減る。
- 【今日のめぐり合わせ】は、同じ場所に別々の組が居合わせた・珍しい場所で知人と鉢合わせた、を機械的に拾ったもの。
  依頼先が被る、街で顔を合わせるはずのない二人が並ぶ——といった偶然を、GMの作為なしに場面の起点として使える。"""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", type=int, default=None, help="作中の日付(省略で session_day.txt の今日)")
    ap.add_argument("--advance", type=int, nargs="?", const=1, default=None,
                    help="今日を N 日進めて session_day.txt を更新する(既定1日)")
    ap.add_argument("--time", default="", help=f"時間帯({'/'.join(SLOTS)})。省略で一日ぶん")
    ap.add_argument("--place", default="", help="この場所だけ表示")
    ap.add_argument("--who", default="", help="この人物の一日を追う")
    ap.add_argument("--check", action="store_true", help="ルーティン表の整合だけ確認する")
    args = ap.parse_args()
    if args.advance is not None:
        set_day(current_day() + args.advance)
        print(f"作中の日付を {current_day()} 日目にした({calendar_of(current_day())['表記']})")
        return 0
    if args.day is None:
        args.day = current_day()

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

    cal = calendar_of(args.day)
    sky = weather_of(args.day)
    head = [f"クロスロードの街の様子({args.day}日目)  {cal['表記']}／空模様:{sky}"]
    for ev in festivals_of(args.day):
        head.append(f"◎ 本日:{ev}")
    if sky == "荒天":
        head.append("　荒天:四大門の出入りが制限され商隊が足止め。空咲の空輸便は止まり、屋外の催事は順延。"
                    "遠出も控えられる(`world/70_calendar_and_climate.md`)")
    elif sky == "小雨〜雨":
        head.append("　雨:露店と散策が静かになり、洗濯場・公衆浴場は混む。街道と危険地域の作業もやや悪化")
    blocks = ["=" * 60] + head + ["=" * 60]
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
