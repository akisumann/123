#!/usr/bin/env python3
"""キャラクターのステータス・スキル合計を機械的に検算するツール。

AI(人)がキャラクターを生成・編集するたびに暗算で検算すると、
どのAIでもズレが起きやすい(評価値にマイナスが混じる・7項目の暗算・
スキル5個の合計など)。このツールはその検算をコードで行い、
レベルとの整合(±2)・スキルLv合計(半分目安)・本文中の自己申告値との
食い違いを機械的に検出する。

検査するのは次の4点:
  1. ステータス7項目の評価値合計 ≒ レベル(±2)
  2. スキルLvの合計 ≒ レベルの半分(±3)
  3. レベルと「◯ランク相当」表記の対応(`world/06_economy.md`のランク表)
  4. SS(規格外)の誤用。SSは五龍のような神話級にのみ使う例外ランク

1ファイルに複数人いるチーム編成ファイル(`- レベル：NN`が複数回出るもの)にも対応し、
「レベル行」ごとに直後のステータス表・スキルLvをひとかたまりとして検算する。

使い方:
    python3 tools/check_character_stats.py                    # 全NPCを検査
    python3 tools/check_character_stats.py characters/npcs/37_tenrai.md  # 1人だけ
"""
from __future__ import annotations
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPC_DIR = os.path.join(ROOT, "characters", "npcs")

RANK_VALUE = {"S": 25, "A": 16, "B": 9, "C": 4, "D": 1, "E": -1, "F": -4}

# 冒険者ランクの帯(`world/06_economy.md`)。レベルとランク表記の食い違いを検出する
GUILD_BANDS = [(10, "F"), (20, "E"), (30, "D"), (40, "C"), (50, "B"), (60, "A"), (100, "S")]
GUILD_RE = re.compile(r"レベル\*{0,2}：\*{0,2}(\d+)\(冒険者ランク基準では([A-S])ランク相当")
# SS(規格外)は五龍のような神話級にのみ使う例外ランク(`rules/02_status_system.md`)
SS_RE = re.compile(r"(?m)^\|\s*(HP|MP|ATK|DEF|INT|SPD|DEX)\s*\|\s*SS\s*\|")
STAT_ORDER = ["HP", "MP", "ATK", "DEF", "INT", "SPD", "DEX"]

STAT_TOLERANCE = 2   # rules/02, rules/10 が定める許容差
SKILL_TOLERANCE = 3  # 「半分程度の目安」なので少し緩め

LEVEL_RE = re.compile(r"^-\s*\*{0,2}レベル\*{0,2}[：:]\s*(\d+)", re.MULTILINE)
RUNTIME_RANDOM_HINT = re.compile(r"起動のたびに|その場でランダムに割り振る")


def find_member_windows(text: str) -> list[tuple[str, int, int]]:
    """「- レベル：NN」の出現ごとに、次の出現(または末尾)までを1人分の範囲として返す。"""
    matches = list(LEVEL_RE.finditer(text))
    windows = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        windows.append((m.group(1), start, end))
    return windows


def member_label(text: str, window_start: int) -> str:
    """直前の`## 名前`/`### 名前`見出しがあればそれを、なければ先頭の`# 名前`を返す。"""
    before = text[:window_start]
    m = re.findall(r"^#{2,3}\s+(.+)$", before, re.MULTILINE)
    if m:
        return m[-1].strip()
    m2 = re.match(r"^#\s+(.+)$", text.lstrip(), re.MULTILINE)
    return m2.group(1).strip() if m2 else "(単独)"


def extract_after_heading(window: str, heading_regex: str) -> str | None:
    m = re.search(heading_regex, window, re.MULTILINE)
    if not m:
        return None
    start = m.end()
    nxt = re.search(r"^#{2,3} ", window[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(window)
    return window[start:end]


RANK_CELL = r"(SS|S|A|B|C|D|E|F)"


def parse_stats(window: str) -> tuple[dict[str, str], int | None]:
    sub = extract_after_heading(window, r"^## ステータス\s*$")
    scope = sub if sub is not None else window
    ranks: dict[str, str] = {}

    # 縦形式: | HP | ランク | 内容 |
    for line in scope.splitlines():
        m = re.match(r"^\|\s*(HP|MP|ATK|DEF|INT|SPD|DEX)\s*\|\s*" + RANK_CELL + r"\s*\|", line)
        if m and m.group(1) not in ranks:
            ranks[m.group(1)] = m.group(2)

    # 横形式: | HP | MP | ATK | DEF | INT | SPD | DEX |  の次行にランクが並ぶ
    if len(ranks) != 7:
        header_re = re.compile(r"^\|\s*HP\s*\|\s*MP\s*\|\s*ATK\s*\|\s*DEF\s*\|\s*INT\s*\|\s*SPD\s*\|\s*DEX\s*\|")
        lines = scope.splitlines()
        for i, line in enumerate(lines):
            if header_re.match(line):
                for j in range(i + 1, min(i + 4, len(lines))):
                    cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    if len(cells) == 7 and all(re.fullmatch(RANK_CELL, c) for c in cells):
                        ranks = dict(zip(STAT_ORDER, cells))
                        break
                break

    if len(ranks) != 7:
        return ranks, None
    if any(r == "SS" for r in ranks.values()):
        return ranks, None
    return ranks, sum(RANK_VALUE[r] for r in ranks.values())


def parse_skills(window: str) -> list[int]:
    sub = extract_after_heading(window, r"^## スキル\s*$")
    scope = sub if sub is not None else window

    # 箇条書き形式: - ◇ スキル名　Lv数字(...)
    lines = [l for l in scope.splitlines() if "◇" in l]
    out = [int(m.group(1)) for l in lines if (m := re.search(r"Lv(\d+)", l))]
    if out:
        return out

    # 表形式: | スキル名 | Lv |
    header_re = re.compile(r"^\|\s*スキル名\s*\|\s*Lv\s*\|")
    lines2 = scope.splitlines()
    for i, line in enumerate(lines2):
        if header_re.match(line):
            for row in lines2[i + 1:]:
                if not row.strip().startswith("|"):
                    break
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if len(cells) == 2 and re.fullmatch(r"\d+", cells[1]):
                    out.append(int(cells[1]))
            break
    return out


def parse_stated(window: str, label_regex: str) -> int | None:
    m = re.search(label_regex + r"[：:]\s*(-?\d+)", window)
    return int(m.group(1)) if m else None


def check_member(level: int, window: str, label: str) -> list[str]:
    problems: list[str] = []

    ranks, stat_sum = parse_stats(window)
    if len(ranks) != 7:
        missing = [s for s in STAT_ORDER if s not in ranks]
        problems.append(f"[{label}] ステータス表が7項目そろっていない(不足:{missing})")
    elif stat_sum is None:
        pass  # SS混在(神話級)。合計チェック対象外
    else:
        diff = stat_sum - level
        if abs(diff) > STAT_TOLERANCE:
            detail = "+".join(f"{s}:{ranks[s]}({RANK_VALUE[ranks[s]]})" for s in STAT_ORDER)
            problems.append(
                f"[{label}] ステータス合計の計算値{stat_sum}がレベル{level}と{diff:+d}ズレ"
                f"(許容±{STAT_TOLERANCE}) [{detail}]"
            )
        stated = parse_stated(window, r"ステータス合計")
        if stated is not None and stated != stat_sum:
            problems.append(f"[{label}] 本文の「ステータス合計：{stated}」が実際の計算値{stat_sum}と食い違い")

    skills = parse_skills(window)
    if not skills:
        problems.append(f"[{label}] スキルのLv表記(`◇ ... Lv数字`)が見つからない")
    else:
        if len(skills) != 5:
            problems.append(f"[{label}] スキル数が5個ではない(実際{len(skills)}個)")
        skill_sum = sum(skills)
        target = level / 2
        if abs(skill_sum - target) > SKILL_TOLERANCE:
            problems.append(
                f"[{label}] スキルLv合計{skill_sum}がレベル{level}の半分({target:.1f})から離れすぎ"
                f"(許容±{SKILL_TOLERANCE})"
            )
        stated_skill = parse_stated(window, r"スキルLv合計")
        if stated_skill is not None and stated_skill != skill_sum:
            problems.append(f"[{label}] 本文の「スキルLv合計：{stated_skill}」が実際の計算値{skill_sum}と食い違い")

    return problems


def guild_band(level: int) -> str:
    for hi, rank in GUILD_BANDS:
        if level <= hi:
            return rank
    return "S"


def check_document(text: str) -> list[str]:
    """ファイル全体に対する検査(レベル↔冒険者ランク、SSの誤用)。"""
    problems = []
    for m in GUILD_RE.finditer(text):
        level, stated = int(m.group(1)), m.group(2)
        correct = guild_band(level)
        if stated != correct:
            problems.append(
                f"Lv{level}は{correct}ランク帯なのに「{stated}ランク相当」と書かれている"
                f"(`world/06_economy.md`のランク表)")
    if SS_RE.search(text):
        problems.append("ステータスにSSが使われている。SSは五龍のような神話級にのみ使う"
                        "例外ランク(`rules/02_status_system.md`)")
    return problems


def check_file(path: str) -> tuple[list[str], bool]:
    """(problems, skipped) を返す。skipped=Trueは検査対象外(起動時ランダム生成など)。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    windows = find_member_windows(text)
    if not windows:
        return ["レベル行(`- レベル：NN`)が見つからない"], False

    if len(windows) == 1 and RUNTIME_RANDOM_HINT.search(text):
        return check_document(text), True  # 起動のたびにランダム割り振りする特殊個体

    problems: list[str] = check_document(text)
    for level_str, start, end in windows:
        level = int(level_str)
        window = text[start:end]
        label = member_label(text, start)
        problems.extend(check_member(level, window, label))
    return problems, False


def iter_target_files(args: list[str]) -> list[str]:
    explicit = [a for a in args if not a.startswith("--")]
    if explicit:
        return [os.path.join(ROOT, p) if not os.path.isabs(p) else p for p in explicit]
    return sorted(
        os.path.join(NPC_DIR, f) for f in os.listdir(NPC_DIR) if f.endswith(".md")
    )


def main() -> int:
    args = sys.argv[1:]
    targets = iter_target_files(args)

    any_problem = False
    skipped = 0
    for path in targets:
        problems, was_skipped = check_file(path)
        if was_skipped:
            skipped += 1
            continue
        if problems:
            any_problem = True
            name = os.path.relpath(path, ROOT)
            print(f"⚠ {name}")
            for p in problems:
                print(f"    - {p}")

    checked = len(targets) - skipped
    if not any_problem:
        note = f"(起動時ランダム生成など{skipped}件は対象外)" if skipped else ""
        print(f"OK: 検査対象{checked}件、ステータス・スキル合計はレベルと整合しています。{note}")
        return 0

    print("\n上記のズレは`rules/10_new_character_format.md`「ステータス生成規則」「スキル生成規則」に照らして"
          "見直すか、意図的な例外なら理由を本文に明記してください。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
