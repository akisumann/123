#!/usr/bin/env python3
"""場所×キャラマップ(72)の「行きつけの店」を、飲食店(49)から生成する。

同じ「誰がどの店の常連か」が三箇所に書かれていた:

    world/crossroad/49_crossroad_dining.md   各店の「常連・顔ぶれ」  ← 本家(手書き)
    world/crossroad/72_place_character_map.md 「行きつけの店」の早見  ← ここを生成する
    characters/npcs/*.md                      各人の「行きつけ」      ← 人物側の記述

手で三つ揃えるのは続かない(実際にずれる)ので、**72は49から機械生成**へ移す。
人物側は各人のファイルに残すが、`tools/check_links.py`が49と突き合わせて食い違いを警告する。

72の該当ブロックは下のマーカーで挟まれている。マーカーの外(宿泊・高級料理店・
店に出ない者・区画ごとの施設)は手書きのまま触らない。
"""
from __future__ import annotations
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DINING = os.path.join(ROOT, "world", "crossroad", "49_crossroad_dining.md")
MAP_FILE = os.path.join(ROOT, "world", "crossroad", "72_place_character_map.md")
NPC_DIR = os.path.join(ROOT, "characters", "npcs")

BEGIN = "<!-- AUTO:行きつけの店 ここから(tools/make_place_map.py が49から生成。手で編集しない) -->"
END = "<!-- AUTO:行きつけの店 ここまで -->"

DISTRICTS = ("中央区", "北区", "東区", "南区", "西区")


def short_names() -> dict[str, str]:
    """ファイル番号 → 短い呼び名。"""
    out = {}
    for fn in sorted(os.listdir(NPC_DIR)):
        if not fn.endswith(".md"):
            continue
        head = open(os.path.join(NPC_DIR, fn), encoding="utf-8").readline().lstrip("# ").strip()
        name = re.sub(r"[(（].*", "", head).strip()      # 「小夜(さよ)」→ 小夜
        if "：" in name:
            name = name.split("：", 1)[1]                # 「盗人姉妹：ロゼとリゼ」→ ロゼとリゼ
        elif "・" in name:
            name = name.split("・")[0]                   # 「クラリス・…」→ クラリス
        out[fn.split("_")[0]] = name
    return out


def head_of(shop_line: str) -> str:
    """常連行から一覧部分だけを切り出す(括弧の外の最初の「。」まで)。

    末尾には「アイアンくんの改修祭もこの界隈」「**職人の溜まり場**」のような
    地の文が続くので、そこに出てくる名前を常連として拾わないための処理。
    """
    depth = 0
    for i, ch in enumerate(shop_line):
        if ch in "(（":
            depth += 1
        elif ch in ")）":
            depth -= 1
        elif ch == "。" and depth == 0:
            return shop_line[:i]
    return shop_line


def split_entries(listing: str) -> list[str]:
    """常連の一覧を、括弧の外の「、」で一項目ずつに割る。"""
    out, depth, buf = [], 0, ""
    for ch in listing:
        if ch in "(（":
            depth += 1
        elif ch in ")）":
            depth -= 1
        if ch == "、" and depth == 0:
            out.append(buf)
            buf = ""
            continue
        buf += ch
    if buf.strip():
        out.append(buf)
    return out


def parse_dining():
    """[(区分, 店名, 区画, 種別ラベル, [ファイル番号…])] を返す。"""
    text = open(DINING, encoding="utf-8").read()
    rows = []
    for block in re.split(r"(?m)^## ", text)[1:]:
        kind = block.splitlines()[0].strip()
        if kind not in ("酒場", "茶屋"):
            continue                                     # 高級料理店は常連を持たない作り
        for sec in re.split(r"(?m)^### ", block)[1:]:
            lines = sec.splitlines()
            shop = lines[0].strip()
            # 見出しは「酒場《赤釘亭》」形式。種別を剥がして店名だけ取る
            # (名前そのものに種別が入る「旅籠前茶屋・一服」は素のまま)。
            shop = re.sub(r"^(酒場|茶屋|宿屋|高級店)《(.+)》$", r"\2", shop)
            desc = " ".join(lines[1:5])
            district = next((d for d in DISTRICTS if d in desc), "")
            label = "深夜酒場" if "深夜酒場" in desc else kind
            m = re.search(r"\*\*常連・顔ぶれ\*\*[：:](.+)", sec)
            if not (district and m):
                print(f"  ⚠ {shop}: 区画または常連行が読めない", file=sys.stderr)
                continue
            names = short_names()
            nums = []
            for entry in split_entries(head_of(m.group(1))):
                found = re.findall(r"characters/npcs/(\d+)_", entry)
                if not found:
                    # リンクを張らずに名前だけ書かれている常連(ミーナ・銀鴉の羽根など)。
                    # 一項目ずつ見るので、他人の注記に紛れた名前(「マモリ(クラリスの供)」の
                    # クラリス、「ミルカ」の中のルカ)を拾ってしまう事故が起きない。
                    found = [num for num, nm in names.items() if nm in entry]
                for num in found:
                    if num not in nums:
                        nums.append(num)
            rows.append((kind, shop, district, label, nums))
    return rows


def render(rows) -> str:
    names = short_names()
    out = []
    for kind in ("酒場", "茶屋"):
        out.append(f"**{kind}**")
        for k, shop, district, label, nums in rows:
            if k != kind:
                continue
            who = "／".join(names.get(n, f"?{n}") for n in nums)
            out.append(f"- **{label}《{shop}》**({district})…{who}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    rows = parse_dining()
    body = render(rows)
    text = open(MAP_FILE, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        print("72_place_character_map.md にマーカーがありません。", file=sys.stderr)
        return 1
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    new = head + BEGIN + "\n" + body + END + tail
    if new != text:
        open(MAP_FILE, "w", encoding="utf-8").write(new)
    print(f"行きつけの店: {len(rows)}店を49から生成した")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
