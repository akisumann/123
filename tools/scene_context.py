#!/usr/bin/env python3
"""場面に必要なcanonを機械抽出して1ブロックへ合成するツール(シーンパック生成)。

GM(AI)がファイルを読み飛ばして記憶や雰囲気で進行するのを防ぐため、
「どのファイルを読むか」をAIに選ばせず、場面の入力(人物・場所・時間帯)から
必要な断片(基本情報・ステータス・スキル・口調・日常/行きつけ・よく接する人物・
場所の顔ぶれ・店の常連・時間帯)をコードで抽出し、まとめて出力する。

GM進行の各場面の前にこれを実行し、出力を読んでから描写する。

人物ファイルを**編集する**前には `--edit 名前` を使う。全文と関連ファイルを出し、
書く前に守ることを併記する(読まずに書く・未検分の記述を指示より優先する・
多面性を一つのタグに畳む、という失敗への歯止め)。

使い方:
    python3 tools/scene_context.py --edit ララ            # 編集前に全文を読む
    python3 tools/scene_context.py --chars 天雷,ツバキ --place 夜鴉の止まり木 --time 宵
    python3 tools/scene_context.py --chars 43,44          # ファイル番号でも指定可
    python3 tools/scene_context.py --place 練兵場          # 場所だけでも可
"""
from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPC_DIR = os.path.join(ROOT, "characters", "npcs")
MAP_FILE = os.path.join(ROOT, "world", "crossroad", "72_place_character_map.md")
DINING_FILE = os.path.join(ROOT, "world", "crossroad", "49_crossroad_dining.md")
CALENDAR_FILE = os.path.join(ROOT, "world", "70_calendar_and_climate.md")

# キャラクターファイルから抜き出す節(この順で出力する)
CHAR_SECTIONS = ["ステータス", "スキル", "口調", "装備", "日常", "よく接する人物"]


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def npc_files() -> list[str]:
    return sorted(
        os.path.join(NPC_DIR, f) for f in os.listdir(NPC_DIR) if f.endswith(".md")
    )


def find_char_file(query: str) -> list[str]:
    """名前(H1行)またはファイル名(番号・ローマ字)でキャラファイルを探す。"""
    q = query.strip()
    hits = []
    for path in npc_files():
        base = os.path.basename(path)
        h1 = read(path).lstrip().splitlines()[0]
        if q.isdigit():
            if base.startswith(q.zfill(2) + "_"):
                hits.append(path)
        elif q.lower() in base.lower() or q in h1:
            hits.append(path)
    return hits


def split_sections(text: str) -> tuple[str, dict[str, str]]:
    """先頭部(最初の`## `まで)と、`## 見出し`ごとの本文を返す。"""
    parts = re.split(r"(?m)^## ", text)
    head = parts[0]
    sections: dict[str, str] = {}
    for chunk in parts[1:]:
        lines = chunk.split("\n", 1)
        title = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""
        sections[title] = body.rstrip()
    return head, sections


def render_char(path: str) -> str:
    text = read(path)
    head, sections = split_sections(text)
    out = [head.rstrip()]
    for want in CHAR_SECTIONS:
        for title, body in sections.items():
            # 「日常」「日常の仕事」のような前方一致も拾う
            if title == want or title.startswith(want):
                out.append(f"## {title}\n{body}")
                break
    return "\n\n".join(out)


def extract_h3_section(path: str, keyword: str) -> list[str]:
    """`### 見出し`にkeywordを含む節を抜き出す。"""
    text = read(path)
    results = []
    for m in re.finditer(r"(?m)^### (.+)$", text):
        title = m.group(1)
        if keyword in title:
            start = m.start()
            nxt = re.search(r"(?m)^#{2,3} ", text[m.end():])
            end = m.end() + (nxt.start() if nxt else len(text) - m.end())
            results.append(text[start:end].rstrip())
    return results


def render_place(place: str) -> str:
    out = []
    map_hits = extract_h3_section(MAP_FILE, place)
    if map_hits:
        out.append("【場所×キャラ対応マップ(72)より】\n" + "\n\n".join(map_hits))
    dining_hits = extract_h3_section(DINING_FILE, place)
    if dining_hits:
        out.append("【飲食店(49)より】\n" + "\n\n".join(dining_hits))
    # 72の「行きつけ早見」からも該当行を拾う(店名部分のみ照合し、説明文への一致は無視)
    for line in read(MAP_FILE).splitlines():
        m = re.match(r"- \*\*(.+?)\*\*", line)
        if m and place in m.group(1):
            out.append("【行きつけ早見(72)より】\n" + line)
            break
    if not out:
        out.append(
            f"(場所「{place}」は72/49に見出しが見つからなかった。"
            "world/crossroad/20_crossroad_city_districts.md 等を直接確認すること)"
        )
    return "\n\n".join(out)


def render_time(time_word: str) -> str:
    text = read(CALENDAR_FILE)
    rows = [
        line for line in text.splitlines()
        if line.startswith("|") and time_word in line
    ]
    if rows:
        return "【時間帯(world/70)より】\n" + "\n".join(rows)
    return f"(時間帯「{time_word}」はworld/70の表に見つからなかった)"


IMPORT_COMMIT = "e4cb333"   # 初回の一括インポート(GPT生成データの取り込み)

EDIT_FOOTER = """【このファイルを書き換える前に守ること】
1. **上の全文を読んでから書く。** 見出しと冒頭のセリフだけで書かない。性格・日常・相互関係・
   ステータス・スキルは、書こうとしている内容と必ず突き合わせる。
2. **一番大きな顔を一つ決め、それを崩さない。** 性格タグを並べるのではなく、
   **どの条件でどの面が出るか**を書く(例:褒められた時だけ照れる、焦ると口調が剥がれる、
   尊大だからこそ隠しきれない)。多面性を平坦な一貫性へ畳むと、その人物ではなくなる。
3. **ステータス・スキルと矛盾させない。** INT:Fの人物に緻密な策を語らせない、など。
4. **ファイルの記述とユーザーの指示が食い違ったら、ユーザーが正しい。**
   このリポジトリには外部AIが生成したまま取り込まれ、ユーザーが目を通していない記述が
   含まれる(`CLAUDE.md`運用ポリシー)。canonだからという理由で指示を上書きしない。
5. 数値を足す・変える時は `tools/generate_character_stats.py` で生成し
   `tools/check_character_stats.py` で検算する。"""


# 全ファイルを一括で触った機械的なコミット(これは「検分された」証拠にならない)
BULK_PATTERNS = ("TL;DR", "summaries", "行きつけ", "配布物", "Import ", "loading layer")


def git_info(path: str) -> str:
    """このファイルの編集履歴(未検分の記述を見分ける手がかり)。

    TL;DR一括挿入のような全ファイル対象の機械的コミットは、内容が検分された
    証拠にならないので分けて数える。
    """
    try:
        log = subprocess.run(
            ["git", "log", "--format=%ad %s", "--date=short", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    except Exception:
        return "(git履歴を取得できなかった)"
    if not log:
        return "(git履歴なし)"
    real = [l for l in log if not any(p in l for p in BULK_PATTERNS)]
    out = [f"編集履歴:全{len(log)}件(うち内容に踏み込んだ編集 {len(real)}件)"]
    if not real:
        out.append("  ※初回インポート以降、内容を検分した編集が一度もない。"
                   "記述は外部AIが生成したまま残っている可能性が高い")
    else:
        out += [f"  {l}" for l in real[:4]]
        if len(real) > 4:
            out.append(f"  …ほか{len(real) - 4}件")
    return "\n".join(out)


def render_edit(query: str) -> str:
    hits = find_char_file(query)
    if not hits:
        return f"(「{query}」は characters/npcs/ に見つからない)"
    if len(hits) > 1:
        return "(複数一致:" + ", ".join(os.path.basename(h) for h in hits) + " — 絞り込んで再実行)"
    path = hits[0]
    text = read(path)
    rel = os.path.relpath(path, ROOT)
    links = sorted(set(re.findall(r"characters/npcs/(\d+_[a-z_]+\.md)", text)) -
                   {os.path.basename(path)})
    out = ["=" * 60,
           f"編集前に読む:{rel}",
           git_info(rel),
           "=" * 60,
           text.rstrip(),
           "-" * 60,
           "【このファイルから参照されている人物】(整合を取る相手)",
           "\n".join(f"- characters/npcs/{l}" for l in links) or "(なし)",
           "-" * 60,
           EDIT_FOOTER]
    return "\n\n".join(out)


FOOTER = """【この場面で必ず守ること(CLAUDE.mdより)】
- 能力が絡む行動は、上記のステータス・スキルの範囲で描写する(高ランクは相応に、低ランクに活躍させない)。
- 戦闘は毎ターン `rules/03_combat_system.md` の判定(スキルLv d ステータスランク)を実際に振り、数値を明示する。
- その場の者同士が互いを知らないなら名前を出さない。セリフは必ず `話者「セリフ」` 形式。
- 場面に人を足す時は、上記の顔ぶれ・常連など既存キャラから出す(8割以上)。"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chars", default="", help="登場人物(カンマ区切り。名前またはファイル番号)")
    ap.add_argument("--place", default="", help="場所名(72/49の見出しに部分一致)")
    ap.add_argument("--time", default="", help="時間帯(朝/昼/夕/宵/夜 など。world/70の表に部分一致)")
    ap.add_argument("--edit", default="", help="人物ファイルを編集する前に全文と注意点を出す")
    args = ap.parse_args()

    if args.edit:
        print(render_edit(args.edit))
        return 0

    if not args.chars and not args.place:
        ap.print_help()
        return 1

    blocks = ["=" * 60, "シーンパック(機械抽出。この内容を読んでから描写すること)", "=" * 60]

    if args.time:
        blocks.append(render_time(args.time))

    if args.place:
        blocks.append(f"◆ 場所:{args.place}\n\n{render_place(args.place)}")

    missing = []
    for q in [c for c in args.chars.split(",") if c.strip()]:
        hits = find_char_file(q)
        if not hits:
            missing.append(q)
            continue
        if len(hits) > 1:
            names = ", ".join(os.path.basename(h) for h in hits)
            blocks.append(f"(「{q}」は複数一致: {names} — 絞り込んで再実行)")
            continue
        blocks.append("-" * 60)
        blocks.append(render_char(hits[0]))

    if missing:
        blocks.append(f"(見つからなかった人物: {', '.join(missing)} — 44_crossroad_nicknames.md で名前を確認)")

    blocks.append("-" * 60)
    blocks.append(FOOTER)
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
