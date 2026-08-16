#!/usr/bin/env python3
"""シナリオの種(75)から、各人物・場所ファイルへ「関わる種」の逆引きを生成する。

75_scenario_seeds.md は 80 以上のファイルへリンクを張っているのに、張り返している
ファイルはほとんど無かった。結果、GM進行中にボルガンのファイルを開いても、彼が絡む
種が5つあることに気づけない——**種が引かれないのはこれが原因**である。

そこで、75 の各種が参照しているファイルの側へ、種の番号と題だけを列挙した節を
機械生成する。人物側・場所側から種へ戻れるようにするのが目的で、中身は 75 にしか
書かない(二重管理を作らない)。

    python3 tools/make_seed_index.py            # 生成/更新
    python3 tools/make_seed_index.py --check    # 差分があれば非ゼロで終了

節はマーカーで挟んだ末尾ブロックとして置く。マーカーの外は触らない。
"""
from __future__ import annotations
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = os.path.join(ROOT, "world", "crossroad", "75_scenario_seeds.md")
NPC_DIR = os.path.join(ROOT, "characters", "npcs")

BEGIN = "<!-- AUTO:関わる種 ここから(tools/make_seed_index.py が75から生成。手で編集しない) -->"
END = "<!-- AUTO:関わる種 ここまで -->"

# 種の本文が「相場」「判定方法」の出典として挙げているだけのファイル。
# 逆引きを置いても場面の役に立たないので外す。
SKIP = {
    "world/06_economy.md",
    "world/09_dungeon_generation.md",
    "world/70_calendar_and_climate.md",
}
SKIP_DIRS = ("rules/",)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def npc_names() -> dict[str, str]:
    """呼び名 → characters/npcs/... の相対パス。

    種の本文はリンクを張らず名前だけ書いていることが多い(「エイダの領分」
    「豊根の薬草供給」など)。リンクだけを見ると、それらの人物には種が一つも
    無いことになってしまうので、名前でも拾う。
    """
    out: dict[str, str] = {}
    for fn in sorted(os.listdir(NPC_DIR)):
        if not fn.endswith(".md"):
            continue
        rel = f"characters/npcs/{fn}"
        text = read(os.path.join(NPC_DIR, fn))
        h1 = text.splitlines()[0].lstrip("# ").strip()
        cands = [h1.split("：")[-1]]
        # 複数人ファイル(銀鴉の羽根)は「### 役割：フルネーム」の各人も拾う
        cands += re.findall(r"(?m)^### .*：(.+)$", text)
        for raw in cands:
            m = re.match(r"([^(（]+)[(（]?([^)）]*)", raw.strip())
            if not m:
                continue
            for name in (m.group(1).split("・")[0], m.group(2)):
                name = name.strip()
                # 見出しが名前ではなく説明文のことがある(「『これだ』と思える主君を〜」)
                if not 2 <= len(name) <= 14 or re.search(r"[「」。、,\s]", name):
                    continue
                out.setdefault(name, rel)
    return out


def parse_seeds() -> list[tuple[str, str, list[str]]]:
    """75 を種ごとに分け、(番号, 題, 参照ファイル一覧) を返す。"""
    names = npc_names()
    out = []
    for block in re.split(r"\n(?=### )", read(SEEDS)):
        m = re.match(r"### (.+)", block)
        if not m:
            continue
        head = m.group(1).strip()
        m2 = re.match(r"^(大?\d+)\.\s*(.+)$", head)
        if not m2:            # 「出す時点で〜」など、種ではない ### 見出し
            continue
        num, title = m2.group(1), m2.group(2).strip()
        files = set(re.findall(r"`((?:characters|world|rules)/[^`]+\.md)`", block))
        prose = re.sub(r"`[^`]*`", "", block)          # リンク部分を除いた地の文
        files |= {rel for name, rel in names.items() if name in prose}
        out.append((num, title, sorted(files)))
    return out


def sort_key(num: str) -> tuple[int, int]:
    """通常の種を先に、初手から大きい案件(大N)を後に、それぞれ番号順。"""
    return (1, int(num[1:])) if num.startswith("大") else (0, int(num))


def build_index() -> dict[str, list[tuple[str, str]]]:
    rev: dict[str, list[tuple[str, str]]] = {}
    for num, title, files in parse_seeds():
        for rel in files:
            if rel in SKIP or rel.startswith(SKIP_DIRS):
                continue
            if os.path.relpath(SEEDS, ROOT).replace(os.sep, "/") == rel:
                continue
            rev.setdefault(rel, []).append((num, title))
    for rel in rev:
        rev[rel].sort(key=lambda t: sort_key(t[0]))
    return rev


def render(entries: list[tuple[str, str]]) -> str:
    lines = [
        BEGIN,
        "",
        "## 関わる種",
        "",
        "`world/crossroad/75_scenario_seeds.md`にある、このファイルが絡む種。"
        "**引き出しであってToDoではない。** 使わないまま放置してよい。",
        "",
    ]
    lines += [f"- **{num}.** {title}" for num, title in entries]
    lines += ["", END]
    return "\n".join(lines)


def apply(rel: str, entries: list[tuple[str, str]], check: bool) -> bool:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        print(f"  ! 参照先が無い: {rel}", file=sys.stderr)
        return False
    text = read(path)
    block = render(entries)
    if BEGIN in text and END in text:
        new = re.sub(
            re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S
        )
    else:
        new = text.rstrip("\n") + "\n\n" + block + "\n"
    if new == text:
        return False
    if not check:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return True


def main() -> int:
    check = "--check" in sys.argv
    rev = build_index()
    changed = [rel for rel, entries in sorted(rev.items()) if apply(rel, entries, check)]
    npc = sum(1 for r in rev if r.startswith("characters/"))
    print(f"関わる種: {len(rev)}ファイル(人物{npc} / 場所・組織{len(rev) - npc})、更新{len(changed)}")
    if check and changed:
        for rel in changed:
            print(f"  差分: {rel}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
