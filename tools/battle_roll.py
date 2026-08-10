#!/usr/bin/env python3
"""戦闘判定のダイスを実際に振るツール(`rules/03_combat_system.md`)。

戦闘は毎ターン「スキルLv d ステータスランク」を実際に振り、数値を明示してから
描写する決まりだが、ここが最も省略されやすい。ステータス表とスキル表を
`characters/npcs/`から読み、出目を一つずつ表示するので、雰囲気で数字を作れなくなる。

出目は毎回変わる本物の乱数(街の配置と違い、戦闘は再現しない)。

使い方:
    python3 tools/battle_roll.py --enemy 骨鳴り墓原 \\
        --act 天雷:超遠隔照準:DEX --act ツバキ:鎖鎌術:DEX --act 氷室:氷装甲:DEF
    python3 tools/battle_roll.py --enemy 50 --act 唯一:広範囲斬撃:ATK --mob 30x3
    python3 tools/battle_roll.py --who 天雷          # その人のステータスとスキルを一覧

`--enemy`は**舞台の名前で指定するのが基本**(赤牙森林・骨鳴り墓原など)。敵戦況値は
敵の見た目ではなく舞台のLv帯で決まるため(rules/03「敵戦況値は舞台のLv帯に合わせて
選ぶ」)、「大型だから80」と分類から入ると、中級の採取地へ上位の数字を置く事故が起きる。
"""
from __future__ import annotations
import argparse
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPC_DIR = os.path.join(ROOT, "characters", "npcs")

RANK_DIE = {"S": 7, "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "F": 1}
STATS = ["HP", "MP", "ATK", "DEF", "INT", "SPD", "DEX"]

# 敵戦況値の目安(rules/03)
ENEMY_LEVEL = {"小型魔物の群れ": 30, "通常モンスター集団": 50, "大型魔物": 80,
               "強力なボス": 120, "災害級存在": 200}

# 舞台のLv帯から引く用(rules/03「敵戦況値は舞台のLv帯に合わせて選ぶ」)。
# 敵の見た目(大型/群れ)ではなく、舞台のLv帯が敵戦況値を決める。
ZONE_LEVEL = {"さざめき平原": 30, "赤牙森林": 50, "苔むし地下遺構": 50,
              "灰岩峡谷": 80, "灰岩坑道": 80, "骨鳴り墓原": 100,
              "星食いのダンジョン": 100,
              "Lv20": 30, "Lv30": 50, "Lv45": 80, "Lv60": 100}
# レベル別モブダイス(rules/03「名前なしの味方」)
MOB_DICE = [(20, 3, 3), (30, 3, 4), (40, 4, 4), (45, 4, 5), (50, 5, 5)]


def find_file(query: str) -> str | None:
    for fn in sorted(os.listdir(NPC_DIR)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(NPC_DIR, fn)
        head = open(path, encoding="utf-8").readline()
        if query in fn or query in head:
            return path
    return None


def parse_character(path: str, member: str = "") -> tuple[dict[str, str], dict[str, int]]:
    """(ステータス, スキル)を読む。複数人ファイルはmemberで人物を絞る。"""
    text = open(path, encoding="utf-8").read()
    head = text.splitlines()[0]
    # 複数人ファイル(銀鴉の羽根・ロゼとリゼ等)は、その人物の記述から後ろだけを見る。
    # 単独ファイルは丸ごと使う(表題に名前が入っているので切り出さない)
    if member and member not in head:
        idx = text.find(member)
        if idx > 0:
            text = text[idx:]

    stats: dict[str, str] = {}
    # 縦持ちの表 `| HP | S | …`
    for m in re.finditer(r"(?m)^\|\s*(HP|MP|ATK|DEF|INT|SPD|DEX)\s*\|\s*([SABCDEF])\s*\|", text):
        stats.setdefault(m.group(1), m.group(2))
    # 横持ちの表 `| HP | MP | … |` / `| S | A | … |`
    if not stats:
        m = re.search(r"(?m)^\|\s*HP\s*\|\s*MP\s*\|.*\n\|[-\s|:]+\n\|(.+)\|", text)
        if m:
            cells = [c.strip() for c in m.group(1).split("|")]
            for name, cell in zip(STATS, cells):
                if cell in RANK_DIE:
                    stats[name] = cell

    skills: dict[str, int] = {}
    for m in re.finditer(r"◇\s*(.+?)[\s　]+Lv(\d+)", text):
        skills[m.group(1).strip()] = int(m.group(2))
    for m in re.finditer(r"(?m)^\|\s*([^|]+?)\s*\|\s*Lv?(\d+)\s*\|", text):
        name = m.group(1).strip()
        if name and name not in ("スキル名", "スキル"):
            skills.setdefault(name, int(m.group(2)))
    return stats, skills


def roll(count: int, faces: int) -> tuple[list[int], int]:
    dice = [random.randint(1, faces) for _ in range(count)]
    return dice, sum(dice)


def mob_dice(level: int) -> tuple[int, int]:
    best = MOB_DICE[0]
    for lv, n, f in MOB_DICE:
        if level >= lv:
            best = (lv, n, f)
    return best[1], best[2]


def resolve_act(spec: str, bonus: dict[str, int]) -> tuple[str, int]:
    """`名前:スキル:ステータス` を判定して(表示行, 戦況変化値)を返す。"""
    parts = spec.split(":")
    if len(parts) < 3:
        return f"- {spec}:書式は 名前:スキル名:ステータス", 0
    who, skill_q, stat = parts[0], parts[1], parts[2].upper()
    path = find_file(who)
    if not path:
        return f"- {who}:characters/npcs/に見つからない", 0
    stats, skills = parse_character(path, who)
    if stat not in stats:
        return f"- {who}:ステータス{stat}が読めない({path})", 0
    hit = [k for k in skills if skill_q in k]
    if not hit:
        return f"- {who}:スキル「{skill_q}」が無い(所持:{'／'.join(skills)})", 0
    skill = hit[0]
    lv, rank = skills[skill], stats[stat]
    dice, total = roll(lv, RANK_DIE[rank])
    add = bonus.get(who, 0)
    line = (f"- {who}　{skill}Lv{lv} × {stat}:{rank} → {lv}d{RANK_DIE[rank]}"
            f" = {dice} = {total}")
    if add:
        line += f"　(補正+{add}) = {total + add}"
    return line, total + add


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--act", action="append", default=[],
                    help="行動 `名前:スキル名:ステータス`(複数可)")
    ap.add_argument("--mob", action="append", default=[],
                    help="名前なしの味方 `Lv30x3` の形式(複数可)")
    ap.add_argument("--enemy", default="", help="敵戦況値。数値か目安の名前(大型魔物 など)")
    ap.add_argument("--bonus", action="append", default=[],
                    help="`名前:+5:理由` 装備補正やAI戦術ボーナス(複数可)")
    ap.add_argument("--who", default="", help="その人物のステータスとスキルを一覧する")
    args = ap.parse_args()

    if args.who:
        path = find_file(args.who)
        if not path:
            print(f"({args.who}は characters/npcs/ に見つからない)")
            return 1
        stats, skills = parse_character(path, args.who)
        print(f"# {os.path.basename(path)}")
        print("ステータス:" + "　".join(f"{k}:{v}(d{RANK_DIE[v]})" for k, v in stats.items()))
        print("スキル:" + "　".join(f"{k}Lv{v}" for k, v in skills.items()))
        return 0

    bonus: dict[str, int] = {}
    reasons = []
    for b in args.bonus:
        p = b.split(":")
        if len(p) >= 2:
            bonus[p[0]] = int(p[1].lstrip("+"))
            reasons.append(f"{p[0]}:+{bonus[p[0]]}" + (f"({p[2]})" if len(p) > 2 else ""))

    lines, total = [], 0
    for spec in args.act:
        line, value = resolve_act(spec, bonus)
        lines.append(line)
        total += value
    for spec in args.mob:
        m = re.match(r"(?:Lv)?(\d+)[x×](\d+)", spec, re.I)
        if not m:
            lines.append(f"- モブ:{spec}は `Lv30x3` の形式で")
            continue
        lv, num = int(m.group(1)), int(m.group(2))
        n, f = mob_dice(lv)
        dice, value = roll(n * num, f)
        lines.append(f"- モブ Lv{lv}×{num}体 → {n * num}d{f} = {dice} = {value}")
        total += value

    print("【このターンの判定】(`rules/03_combat_system.md`)")
    print("\n".join(lines))
    if reasons:
        print("補正の内訳:" + "／".join(reasons))
    print(f"\n味方の戦況変化値 合計 = {total}")

    if args.enemy:
        enemy = ENEMY_LEVEL.get(args.enemy) or ZONE_LEVEL.get(args.enemy)
        if enemy is None:
            enemy = int(args.enemy) if args.enemy.isdigit() else 0
        if args.enemy in ZONE_LEVEL:
            label = f"{args.enemy}のLv帯相当"
        elif args.enemy in ENEMY_LEVEL:
            label = args.enemy
        else:
            label = f"敵戦況値{enemy}"
        diff = total - enemy
        ratio = abs(diff) / enemy if enemy else 0
        size = "小さい" if ratio < 0.25 else ("中程度" if ratio < 0.75 else "大きい")
        print(f"敵戦況値 = {enemy}({label})")
        print(f"差分 = {diff:+d}　差分は敵戦況値の{ratio * 100:.0f}%＝{size}")
        print("""
差分の読み方(rules/03。ダメージではなく戦況の動き方):
- 小さい…戦況はほとんど変化しない。軽い攻防や小さな有利・不利程度。
- 中程度…戦況が明確に変化する。押し返す、負傷する、包囲される、突破口を開くなど。
- 大きい…戦局が大きく動く。敵主力の崩壊、撤退、制圧、討伐など決定的な出来事。
※上の割合は読み違え防止の目安で、描写の規模は差分の大小に対応させること。
※敵戦況値は敵の見た目(大型/群れ)ではなく**舞台のLv帯**で決める(rules/03)。
　Lv10〜20＝30／Lv25〜35＝50／Lv40〜50＝80／Lv55〜70＝100。
　この系は上で飽和する:1人1ターンの上限は7d7≒28、4人でも天井は112前後。
　120以上はレベルでは届かず、頭数・装備補正・戦術ボーナスで超える領域。
　Lv帯を超える数字を置く時は「その地域に本来いない異常個体」として描写すること。""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
