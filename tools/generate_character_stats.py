#!/usr/bin/env python3
"""ステータス・スキルの数値をAIの雰囲気任せにせず、コードで決定するツール。

「1項目ずつ計算しながら割り振る」と指示しても、実際にはAIはランクを
雰囲気で選び、あとから帳尻合わせの説明を付けるだけになりやすい。
このツールはその逆で、**AIは「どのステータスを強くしたいか」という
優先順位(＝キャラクターらしさ)だけを決め、実際のランク配分と数値は
すべてこのツールが計算する。** AIは出力された数値をそのまま使い、
各項目の「理由」文とスキル名だけを埋める。

使い方:
    python3 tools/generate_character_stats.py --level 18 \\
        --stats SPD,INT,DEX,HP,DEF,ATK,MP

    --stats は7項目(HP,MP,ATK,DEF,INT,SPD,DEX)を、
    強くしたい順(得意→不得意)に**全部**並べる。

    スキル名を指定したい場合:
    python3 tools/generate_character_stats.py --level 18 \\
        --stats SPD,INT,DEX,HP,DEF,ATK,MP \\
        --skills 近道走破,荷物運搬術,顔利き,地理感覚,愛想笑い
"""
from __future__ import annotations
import argparse
from itertools import combinations_with_replacement

STAT_ORDER = ["HP", "MP", "ATK", "DEF", "INT", "SPD", "DEX"]
LETTERS = ["S", "A", "B", "C", "D", "E", "F"]  # 強い順
VALUES = [25, 16, 9, 4, 1, -1, -4]             # LETTERSと対応
STAT_TOLERANCE = 2
SKILL_TOLERANCE = 3


def allocate_stats(level: int) -> list[str]:
    """優先順位(強い→弱い)に沿って、レベル±2に収まるランク列を1つ選ぶ。"""
    target_lo, target_hi = level - STAT_TOLERANCE, level + STAT_TOLERANCE
    best = None
    best_score = None
    for combo in combinations_with_replacement(range(7), 7):
        s = sum(VALUES[i] for i in combo)
        if target_lo <= s <= target_hi:
            diff = abs(s - level)
            distinct = len(set(combo))  # 使うランク種が多いほど個性が出る
            score = (diff, -distinct, combo)
            if best_score is None or score < best_score:
                best_score = score
                best = combo
    if best is None:
        # レベルが極端で±2に収まらない場合は最も近いものを許容超過で返す
        best = min(
            combinations_with_replacement(range(7), 7),
            key=lambda c: abs(sum(VALUES[i] for i in c) - level),
        )
    return [LETTERS[i] for i in best]


def allocate_skills(level: int, n: int = 5) -> list[int]:
    """優先順位(強い→弱い)に沿って、レベル半分に近いスキルLv列を1つ選ぶ。"""
    target = level / 2
    t = max(n, round(target))  # 各1以上を保証
    base, rem = divmod(t, n)
    levels = [base + 1] * rem + [base] * (n - rem)
    return levels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--stats", required=True, help="7項目を得意→不得意の順にカンマ区切りで(例:SPD,INT,DEX,HP,DEF,ATK,MP)")
    ap.add_argument("--skills", default=None, help="スキル名5個をカンマ区切りで(省略時は仮名)")
    args = ap.parse_args()

    priority = [s.strip().upper() for s in args.stats.split(",")]
    if sorted(priority) != sorted(STAT_ORDER):
        print(f"エラー: --stats は{STAT_ORDER}の7項目を過不足なく指定してください(入力:{priority})")
        return 1

    ranks = allocate_stats(args.level)
    stat_sum = sum(VALUES[LETTERS.index(r)] for r in ranks)
    diff = stat_sum - args.level

    print(f"## ステータス(Lv{args.level}、優先順位:{'>'.join(priority)})\n")
    print("| 項目 | ランク | 内容 |")
    print("|---|---|---|")
    for stat, rank in zip(priority, ranks):
        print(f"| {stat} | {rank} | (ここに理由を書く) |")
    tag = "diff±0" if diff == 0 else f"diff{diff:+d}で許容範囲内"
    print(f"\nステータス合計：{stat_sum}(Lv{args.level}、{tag})\n")

    skill_names = (
        [s.strip() for s in args.skills.split(",")] if args.skills else [f"スキル{i+1}" for i in range(5)]
    )
    if len(skill_names) != 5:
        print(f"エラー: --skills は5個指定してください(入力:{len(skill_names)}個)")
        return 1

    skill_levels = allocate_skills(args.level)
    skill_sum = sum(skill_levels)

    print("## スキル\n")
    for name, lv in zip(skill_names, skill_levels):
        print(f"- ◇ {name}　Lv{lv}(ここに説明を書く)")
    half = args.level / 2
    match = "と一致" if skill_sum == half else "とほぼ一致" if abs(skill_sum - half) <= SKILL_TOLERANCE else "から離れすぎ"
    print(f"\nスキルLv合計：{skill_sum}(Lv{args.level}の半分{match})")

    print(
        "\n※この出力の数値(ランク・スキルLv・合計)は変更しないこと。"
        "変えていいのは「内容」欄の理由文・スキル説明・スキル名のみ。"
        "数値を直接編集した場合は必ず`tools/check_character_stats.py`で再検算する。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
