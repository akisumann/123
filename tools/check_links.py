#!/usr/bin/env python3
"""ファイル間の相互参照(`path/to/file.md`)が実在するか検査する。

設定ファイルは互いを `characters/npcs/07_dario_langford.md` のように参照し合う。
参照先が存在しないと、AI は「探しても見つからない」状態になり進行が崩れる。
このツールで壊れた参照(リンク切れ)を洗い出す。

  python3 tools/check_links.py          # リンク切れを一覧
  python3 tools/check_links.py --strict # リンク切れがあれば終了コード1(CI用)
"""
from __future__ import annotations
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 検査対象の「参照元」から除くファイル。
# - 生成物(他ファイルの複製): 123_all.md / DIGEST.md / INDEX.md
# - 作業ログ: PROGRESS.md はファイル名を略記(basename のみ等)で記録するため、
#   リンク整合の対象外とする(正典本体の参照だけを検査したい)。
SKIP_FILES = {"123_all.md", "DIGEST.md", "INDEX.md", "PROGRESS.md"}

# `...md` 形式のパス参照を拾う(バッククォート有無どちらも)。
REF = re.compile(r'([A-Za-z0-9_./]+\.md)')


def all_md():
    """参照元として検査する正典ファイル(tools/配下は対象外)。"""
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "tools")]
        for n in sorted(fns):
            if n.endswith(".md"):
                yield os.path.relpath(os.path.join(dp, n), ROOT).replace(os.sep, "/")


def link_targets():
    """参照先として実在を認めるファイル。tools/配下(README等)も含める。"""
    out = set(all_md())
    tools_dir = os.path.join(ROOT, "tools")
    if os.path.isdir(tools_dir):
        out |= {f"tools/{n}" for n in os.listdir(tools_dir) if n.endswith(".md")}
    return out


def main() -> int:
    existing = set(all_md())
    targets = link_targets()
    broken = []  # (source, ref)
    for rel in existing:
        if rel in SKIP_FILES:
            continue
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            text = f.read()
        for m in set(REF.findall(text)):
            # 自明な非参照を除外
            if m.startswith(("http://", "https://")):
                continue
            # 相対でルート基準のパスとして解決
            norm = m.lstrip("./")
            if norm in targets:
                continue
            # ルート直下ファイル(CLAUDE.md 等)への言及も existing に含まれる
            broken.append((rel, m))

    if not broken:
        print(f"OK: リンク切れなし({len(existing)} ファイルを検査)")
        return check_hangouts() or check_unique_claims()

    # 参照先ごとにまとめて表示
    by_ref = {}
    for src, ref in broken:
        by_ref.setdefault(ref, []).append(src)
    print(f"⚠ リンク切れ {len(by_ref)} 種類 / 参照元 {len(broken)} 箇所:\n")
    for ref in sorted(by_ref):
        print(f"  ✗ {ref}")
        for src in sorted(set(by_ref[ref])):
            print(f"      ← {src}")
    return 1 if "--strict" in sys.argv else 0


def check_hangouts() -> int:
    """各NPCの「行きつけ」と、飲食店(49)の「常連・顔ぶれ」が食い違っていないか見る。

    同じ事実が人物側と店側の二箇所にあるため、片方だけ書き換えると静かにずれる。
    (実際に、店側にしかいない常連・人物側にしかない行きつけが溜まっていた。)
    """
    import make_place_map as mp
    rows = mp.parse_dining()
    shop_members = {shop: set(nums) for _, shop, _, _, nums in rows}
    names = mp.short_names()
    bad = []
    for fn in sorted(os.listdir(mp.NPC_DIR)):
        if not fn.endswith(".md"):
            continue
        num = fn.split("_")[0]
        text = open(os.path.join(mp.NPC_DIR, fn), encoding="utf-8").read()
        m = re.search(r"\*\*行きつけ\*\*[：:](.+)", text)
        if not m:
            continue
        for shop, members in shop_members.items():
            if shop in m.group(1) and num not in members:
                bad.append((names.get(num, num), shop))
    if not bad:
        print("OK: 行きつけと常連の食い違いなし")
        return 0
    print(f"⚠ 行きつけ／常連の食い違い {len(bad)} 件"
          "(人物側に店名があるのに、49のその店の常連に入っていない):")
    for who, shop in bad:
        print(f"  ✗ {who} … {shop}"
              f"  → world/crossroad/49_crossroad_dining.md の《{shop}》へ追記するか、"
              "人物側の行きつけを直す")
    return 1



# 「これは街に一つしかない」と主張している言い回し。
# 同じ物を二箇所で別々に作ってしまう事故(回復杖の件)を、目視できる一覧にして防ぐ。
# 「街で唯一」は人にも掛かる(「街で唯一これを振れる者」「街で唯一の総合病院」)ため
# 入れていない。物の一意性を主張する言い回しだけを拾う。
UNIQUE_RE = re.compile(
    r"(?:街に|世界に|他に)?[一１]本しかな[いく]|[一１]つしかな[いく]|"
    r"複製ではなく現物|他に例がない|現存する唯一|一点しか(?:存在し)?な[いく]")
# 一意性の主張の近くに出てくる「物」の名前。ここが一致したら同じ物の疑い。
THING_RE = re.compile(r"[杖剣槍刀弓盾鎧兜鍵書板玉珠石環鎖笛鏡札像柱門]")


def check_unique_claims() -> int:
    """「街に一つしかない」と書かれた物を一覧にし、種類が重なったら警告する。"""
    hits = []          # (ファイル, 行番号, 抜粋, 物の字)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "__"))
                       and d not in ("tools",)]
        for name in sorted(filenames):
            if not name.endswith(".md") or name.startswith(
                        ("123_", "DIGEST", "INDEX", "PROGRESS", "CHARACTERS")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
            heading = ""
            for i, line in enumerate(open(os.path.join(dirpath, name),
                                          encoding="utf-8"), 1):
                if line.startswith("#"):
                    heading = line.lstrip("# ").strip()
                m = UNIQUE_RE.search(line)
                if not m:
                    continue
                near = line[max(0, m.start() - 40):m.end() + 40]
                # 「何が一つしかないのか」は見出しに書いてあることが多い
                # (48は本文ではなく「## 大地龍の杖」の側に杖がある)ので、
                # 直近の見出しも文脈に含める。
                things = set(THING_RE.findall(heading + near))
                hits.append((rel, i, f"[{heading}] {near.strip()}", things))

    dup = {}
    for rel, i, near, things in hits:
        for t in things:
            dup.setdefault(t, []).append((rel, i, near))
    clash = {t: v for t, v in dup.items() if len({r for r, _, _ in v}) > 1}
    if not clash:
        print(f"OK: 一意な物の重複なし(一意性の主張 {len(hits)} 箇所を照合)")
        return 0
    print(f"⚠ 同じ種類の「一つしかない物」が別々のファイルにあります "
          f"({len(clash)} 種類)。同じ物を二重に作っていないか確認してください:")
    for t, v in sorted(clash.items()):
        print(f"  ✗ 「{t}」")
        for rel, i, near in v:
            print(f"      {rel}:{i}  …{near}…")
    return 1



if __name__ == "__main__":
    raise SystemExit(main())
