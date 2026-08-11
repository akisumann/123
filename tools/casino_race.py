#!/usr/bin/env python3
"""魔導盤レースを実際に走らせるツール(`world/crossroad/29_crossroad_magic_board_race.md`)。

カジノの賭けは物語の都合で決めない決まりだが(`world/crossroad/28_crossroad_casino.md`)、
レースだけは「倍率を重み付けして1着を引く」形になっていて、**倍率を決めた時点で勝率が
決まってしまう**という逆立ちがあった。このツールは順序を戻す。

    出走6匹と地形を引く → 実際に何千回も走らせる → 勝率が出る → そこから倍率を付ける
                                                  → 本番を1回走らせる

そのため倍率は「運営がそう見ている数字」であって、真の勝率とは一致しない。
**脚質(区画ごとの得手不得手)は非公開で、倍率に反映されない。** 出走表に載るのは系統と
地形だけなので、脚質を覚えている常連だけが、倍率の歪みを取りに行ける。

使い方:
    python3 tools/casino_race.py --day 93 --race 3            # 出走表(客が見る情報)
    python3 tools/casino_race.py --day 93 --race 3 --run      # 本番を走らせる
    python3 tools/casino_race.py --day 93 --race 3 --run --reveal   # 脚質も見る(GM用)
    python3 tools/casino_race.py --list                       # 幻獣22種の隠し脚質一覧
"""
from __future__ import annotations
import argparse
import hashlib
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 走りの定数(race.js の考え方を借りている) ---------------------------------
GOAL = 100.0
STEP = (1.2, 6.8)      # 1歩の進み(幅が広いほど運の比重が上がる)
LEGS = 4               # 四区画
FAM_GOOD, FAM_BAD = 1.16, 0.88   # 系統が地形と合う/合わない(公開情報)
RUN_GOOD, RUN_BAD = 1.15, 0.87   # 脚質が区画と合う/合わない(非公開・倍率に載らない)
EVENT_P_HAZARD = 0.15  # 第三区画(妨害区画)で何かが起きる割合
EVENT_P_OTHER = 0.05   # それ以外の区画
TAKE = 0.80            # 控除後の払い戻し率(倍率＝勝率の逆数×これ)
TRIALS = 4000          # 倍率を出すための試走回数
POP = 0.10             # 人気による倍率の揺れ(±この割合)
ODDS_MAX = 30.0        # これ以上は付かない(穴にも義理の金が入るため)

# 有利と不利が完全対称なので、演出を足しても期待値は動かない
EVENTS = [(6, "ぐんと伸びた"), (4, "外から追い上げた"), (3, "前に出た"),
          (-3, "よそ見をした"), (-4, "つまずいた"), (-6, "立ち止まった")]

# --- 地形(第二区画で引く。第三区画はこれを引き継いで妨害が乗る) -----------------
# どの系統も「得意」に1回・「苦手」に1回ずつしか出てこない。
# 長く張り続ければ系統による有利不利は消える、という形で公平性を担保する。
TERRAIN = [
    ("草原",     "草原系", "水場系"),
    ("水路",     "水場系", "砂地系"),
    ("岩場",     "岩場系", "泥濘系"),
    ("砂地",     "砂地系", "森道系"),
    ("霧",       "霧幻系", "草原系"),
    ("ぬかるみ", "泥濘系", "岩場系"),
    ("森道",     "森道系", "霧幻系"),
]

# 第三区画に乗る妨害(描写用。効果は EVENTS 側で一律に処理する)
HAZARD = ["落石", "突風", "水流", "雷", "幻影", "足場崩れ", "視界不良"]

# 区画の性格(脚質の得手不得手が乗る先)
LEG_NAME = ["第一区画(平地直線・初速)", "第二区画(地形変化)",
            "第三区画(地形＋妨害)", "第四区画(平地コーナー・伸び)"]

# --- 幻獣22種 -----------------------------------------------------------------
# (種族, 系統[公開], 得意区画[非公開], 苦手区画[非公開], 出走名に使う和語の候補)
# 系統は`world/crossroad/29`の「幻獣一覧」の地形適性から、
# 得意/苦手区画は同じ行の脚の説明から起こしている。
BEASTS = [
    ("狼",     "草原系", 4, 2, ["夜駆け", "群れ影", "追込"]),
    ("鹿",     "森道系", 2, 1, ["跳躍", "夜鹿", "枝角"]),
    ("鷹",     "岩場系", 1, 3, ["風羽", "高翔", "断崖"]),
    ("蛇",     "水場系", 4, 1, ["沼這い", "曲身", "水縄"]),
    ("亀",     "砂地系", 3, 1, ["鈍甲", "不動", "重殻"]),
    ("狐",     "霧幻系", 3, 1, ["幻惑", "七化け", "分かれ道"]),
    ("馬",     "草原系", 1, 4, ["疾走", "直線", "先掛け"]),
    ("虎",     "岩場系", 2, 4, ["荒岩", "突破", "牙走り"]),
    ("兎",     "草原系", 1, 3, ["跳ね耳", "初足", "小回り"]),
    ("蜥蜴",   "砂地系", 2, 1, ["岩肌", "壁這い", "砂走り"]),
    ("蛙",     "泥濘系", 2, 4, ["湿地", "跳ね泥", "水搔き"]),
    ("蟹",     "水場系", 3, 1, ["横這い", "硬爪", "波打ち"]),
    ("蜘蛛",   "森道系", 3, 1, ["糸掛け", "枝渡り", "八脚"]),
    ("山羊",   "岩場系", 2, 1, ["崖登り", "岩角", "坂駆け"]),
    ("猪",     "草原系", 3, 4, ["突進", "藪破り", "直進"]),
    ("蝶",     "霧幻系", 4, 3, ["風紋", "霞翅", "幻影"]),
    ("魚",     "水場系", 2, 4, ["水路", "銀鱗", "流れ乗り"]),
    ("小竜",   "砂地系", 1, 3, ["火花", "暴走", "小翼"]),
    ("小精霊", "霧幻系", 2, 3, ["属光", "宿り火", "揺らぎ"]),
    ("スライム", "泥濘系", 3, 1, ["泥被り", "衝撃殺し", "狭路"]),
    ("猫",     "森道系", 3, 1, ["着地", "身躱し", "曲がり"]),
    ("貂",     "泥濘系", 4, 2, ["軽身", "小抜け", "纏い"]),
]

KANA = ["コメット", "ガロップ", "バスター", "シルフィ", "ドレイク", "ノクターン",
        "クロウル", "ジャンパー", "スカイラーク", "タスク", "ブリーズ", "ロウラー",
        "シェイド", "グリット", "ランブル", "ミラージュ"]


def rng(*parts) -> random.Random:
    """入力から決まる固定乱数(`tools/day_plan.py`と同じ作り)。"""
    key = "|".join(str(p) for p in parts)
    return random.Random(int(hashlib.md5(key.encode("utf-8")).hexdigest()[:16], 16))


def leg_at(x: float) -> int:
    """0〜3を返す。"""
    i = int(x / (GOAL / LEGS))
    return 0 if i < 0 else (LEGS - 1 if i >= LEGS else i)


def build_card(day: int, race: int):
    """出走6匹と四区画の地形を引く。同じ(day, race)なら毎回同じ。"""
    r = rng("magic-board-race", day, race)
    field = r.sample(BEASTS, 6)
    t2 = r.choice(TERRAIN)                       # 第二区画で引いた地形
    hazard = r.sample(HAZARD, 2)                 # 第三区画で乗る妨害
    kana = r.sample(KANA, 6)
    entries = []
    for i, (sp, fam, up, down, words) in enumerate(field, 1):
        name = r.choice(words) + kana[i - 1]
        entries.append({"枠": i, "出走名": name, "種": sp, "系統": fam,
                        "得意区画": up, "苦手区画": down})
    return entries, t2, hazard


def run_once(entries, terrain, r: random.Random, use_style: bool):
    """1レース走らせて、着順と区画ごとの通過順位を返す。

    use_style=False で走らせたものが「客に見える情報だけで読んだ勝率」になる。
    """
    _, good_fam, bad_fam = terrain
    lanes = [{"i": i, "x": 0.0} for i in range(len(entries))]
    done, passing = [], {1: None, 2: None, 3: None}
    while len(done) < len(lanes):
        reached = []
        for ln in lanes:
            if ln["i"] in done:
                continue
            e = entries[ln["i"]]
            leg = leg_at(ln["x"])              # 0-origin
            d = r.uniform(*STEP)
            # 系統は地形のある第二・第三区画だけで効く(公開情報)
            if leg in (1, 2):
                if e["系統"] == good_fam:
                    d *= FAM_GOOD
                elif e["系統"] == bad_fam:
                    d *= FAM_BAD
            # 脚質は四区画すべてに効く(非公開)
            if use_style:
                if e["得意区画"] == leg + 1:
                    d *= RUN_GOOD
                elif e["苦手区画"] == leg + 1:
                    d *= RUN_BAD
            p = EVENT_P_HAZARD if leg == 2 else EVENT_P_OTHER
            if r.random() < p:
                d += EVENTS[r.randrange(len(EVENTS))][0]
            ln["x"] = max(0.0, ln["x"] + d)
            if ln["x"] >= GOAL:
                reached.append(ln)
        for k in (1, 2, 3):
            if passing[k] is None and all(ln["x"] >= GOAL / LEGS * k for ln in lanes):
                passing[k] = [ln["i"] for ln in sorted(lanes, key=lambda a: -a["x"])]
        reached.sort(key=lambda a: -a["x"])
        for ln in reached:
            ln["x"] = GOAL
            done.append(ln["i"])
    return done, passing


def odds_for(entries, terrain, day, race):
    """脚質を伏せたまま試走して勝率を出し、倍率へ直す。

    最後に人気の揺れを乗せる。同じ系統が二頭出れば読みの上では区別が付かないが、
    賭場の倍率は客の金の寄り方で必ずわずかにずれるため、**同値にはならない。**
    """
    r = rng("odds", day, race)
    wins = [0] * len(entries)
    for _ in range(TRIALS):
        order, _ = run_once(entries, terrain, r, use_style=False)
        wins[order[0]] += 1
    pop = rng("pop", day, race)
    out = []
    for w in wins:
        p = max(w / TRIALS, 0.02)
        o = TAKE / p * (1.0 + pop.uniform(-POP, POP))
        out.append(round(min(max(o, 1.5), ODDS_MAX), 1))
    # 賭場の板に同じ数字は二つ並ばない。重なったら0.1ずつずらす。
    seen = set()
    for i, o in enumerate(out):
        while round(o, 1) in seen:
            o += 0.1
        out[i] = round(o, 1)
        seen.add(out[i])
    return out, [w / TRIALS for w in wins]


def band(o: float) -> str:
    if o <= 2.0:
        return "大本命"
    if o <= 4.0:
        return "有力"
    if o <= 8.0:
        return "中穴"
    if o < 30.0:
        return "大穴"
    return "超大穴"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", type=int, help="作中の日付(tools/session_day.txt)")
    ap.add_argument("--race", type=int, default=1, help="第何競走か(既定1)")
    ap.add_argument("--run", action="store_true", help="本番を走らせて着順を出す")
    ap.add_argument("--reveal", action="store_true", help="非公開の脚質も表示する(GM用)")
    ap.add_argument("--list", action="store_true", help="幻獣22種の系統と隠し脚質を一覧")
    args = ap.parse_args()

    if args.list:
        print("# 幻獣22種(系統は公開／得意・苦手区画は**非公開**)")
        print(f"{'種':<6}{'系統':<7}{'得意区画':<9}苦手区画")
        for sp, fam, up, dn, _ in BEASTS:
            print(f"{sp:<6}{fam:<7}第{up}区画{'':<5}第{dn}区画")
        print("\n" + "\n".join(f"  {n}　得意={g}／苦手={b}" for n, g, b in TERRAIN))
        return 0

    day = args.day
    if day is None:
        p = os.path.join(ROOT, "tools", "session_day.txt")
        day = int(open(p, encoding="utf-8").read().strip()) if os.path.exists(p) else 1

    entries, terrain, hazard = build_card(day, args.race)
    odds, true_p = odds_for(entries, terrain, day, args.race)

    tname, tgood, tbad = terrain
    print(f"第{args.race}競走・出走魔獣　({day}日目)")
    print(f"　第一区画:平地直線／第二区画:**{tname}**／"
          f"第三区画:{tname}＋{'・'.join(hazard)}／第四区画:平地コーナー")
    print(f"　この地形で伸びるのは{tgood}、詰まるのは{tbad}\n")
    print(f"{'枠':<3}{'出走名':<18}{'系統':<7}{'区分':<7}単勝倍率")
    for e, o in zip(entries, odds):
        print(f"{e['枠']:<3}{e['出走名']:<18}{e['系統']:<7}{band(o):<7}×{o}")
    print("\n最低賭け金は一頭につき100G。複数へ分散してもよい。")

    if args.reveal:
        print("\n【GM専用・客には見えない】")
        for e, o, p in zip(entries, odds, true_p):
            print(f"  {e['出走名']}({e['種']})　得意=第{e['得意区画']}区画／"
                  f"苦手=第{e['苦手区画']}区画　"
                  f"倍率の元になった読み勝率={p * 100:.1f}%")
        print("  ※上の勝率は脚質を伏せて出したもの。本番は脚質込みで走るのでズレる。")

    if args.run:
        order, passing = run_once(entries, terrain, rng("run", day, args.race), True)
        print("\n【本番】")
        for k in (1, 2, 3):
            if passing[k]:
                print(f"　{LEG_NAME[k - 1]}通過　"
                      + " → ".join(entries[i]["出走名"] for i in passing[k]))
        print("　── 着順 ──")
        for place, i in enumerate(order, 1):
            e = entries[i]
            mark = "★" if place == 1 else "　"
            print(f"　{mark}{place}着　{e['出走名']}　(×{odds[i]})")
        w = order[0]
        print(f"\n　単勝的中は枠{entries[w]['枠']}「{entries[w]['出走名']}」"
              f"　100Gにつき{int(100 * odds[w])}G")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
