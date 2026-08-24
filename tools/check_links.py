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
        return (
            check_hangouts()
            or check_unique_claims()
            or check_overrides()
            or check_quest_ranks()
            or check_npc_counts()
            or check_mutual_contacts()
        )

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



def check_mutual_contacts() -> int:
    """「よく接する人物」が片側にしか書かれていない線を数える(報告のみ)。

    **これは失敗ではない。** 関係は対称とは限らないためである。滞在中の修道女が
    領主を挙げるのは自然でも、領主の側が彼女を挙げるとは限らない。黒針会の幹部が
    「察した上でスルーしてくる相手」を挙げていても、相手側には書く理由が無い。
    **格下から格上への線、片方だけが意識している線は、片側で正しい。**

    それでも数を見せるのは、**両側に書くべき線を書き忘れた場合**(同格の相棒、
    同じ店の常連同士、取引相手など)がこの中に紛れるためである。増減を眺めて、
    心当たりのあるものだけ直せばよい。一覧は `--contacts` で出る。
    """
    import make_place_map as mp

    npc_dir = mp.NPC_DIR
    files = [f for f in sorted(os.listdir(npc_dir)) if f.endswith(".md")]
    names = {}
    contacts = {}
    for fn in files:
        text = open(os.path.join(npc_dir, fn), encoding="utf-8").read()
        names[fn] = text.split("\n")[0].lstrip("# ").strip()
        m = re.search(r"^## よく接する人物\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        sec = m.group(1) if m else ""
        contacts[fn] = {os.path.basename(x) for x in
                        re.findall(r"characters/npcs/([0-9]+_[A-Za-z0-9_]+\.md)", sec)}

    known = set(files)
    bad = []
    for fn in files:
        for other in sorted(contacts[fn]):
            if other not in known:
                continue          # 存在しないパスはリンク切れ検査の担当
            if fn not in contacts.get(other, set()):
                bad.append((names[fn], fn, names.get(other, other), other))

    pairs = sum(len(v) for v in contacts.values())
    if not bad:
        print(f"OK: よく接する人物は全て相互(のべ {pairs} 本の線を照合)")
        return 0
    print(f"— よく接する人物:のべ {pairs} 本のうち {len(bad)} 本が片側のみ"
          "(関係は対称とは限らないので、これ自体は異常ではない。"
          "一覧は --contacts)")
    if "--contacts" in sys.argv:
        for a, af, b, bf in bad:
            print(f"    {a}({af}) → {b}({bf})")
    return 0


OVERRIDE = re.compile(r"([ぁ-んァ-ヶ一-龥ー]{2,8})(?:という|と言う)より")


def check_overrides() -> int:
    """「〇〇というより××」が、同じファイルで繰り返し使われている語を否定していないか。

    銀雪の口調欄が「のんびりというより深刻さの基準がずれている」と書いていた一方、
    同じファイルの日常・行きつけ・よく接する人物の4箇所は「のんびり」と書いていた。
    **後から足した一行だけが読まれて、元の4箇所が死ぬ**——という壊れ方をする。

    否定された語がそのファイル内で他に2回以上出てくる場合だけ警告する。
    「代表というより世話役」のように、否定するためにだけ使っている語は素通りさせる。
    """
    hits = []
    for rel in all_md():
        # 生成物(全部載せ・名簿)は語の出現数が合算されて意味を成さない
        if rel in SKIP_FILES or os.path.basename(rel).startswith(
                ("123_", "DIGEST", "INDEX", "PROGRESS", "CHARACTERS")):
            continue
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            text = f.read()
        for m in OVERRIDE.finditer(text):
            word = m.group(1)
            others = text.count(word) - 1
            if others >= 2:
                line = text[: m.start()].count("\n") + 1
                hits.append((rel, line, word, others))
    if not hits:
        print("OK: 繰り返し使われている語を「〜というより」で上書きしている箇所なし")
        return 0
    print(f"⚠ 「〜というより」が、同ファイルで2回以上使われている語を否定している箇所 {len(hits)} 件:")
    for rel, line, word, n in hits:
        print(f"  ・{rel}:{line}  「{word}」は同ファイルに他{n}箇所ある")
    print("   → 言い換えた側だけが読まれて元の記述が死ぬ。両立させるか、元の語へ揃える。")
    return 0


# world/06_economy.md「冒険者向け依頼報酬」のランク別報酬帯。
QUEST_BAND = {"F": (500, 1000), "E": (1000, 2000), "D": (2000, 4000),
              "C": (4000, 8000), "B": (8000, 16000), "A": (16000, 32000),
              "S": (32000, 10 ** 9)}
QUEST_BOARDS = ("world/crossroad/64_danger_zone_quest_board.md",
                "world/crossroad/65_dungeon_quest_board.md",
                "world/crossroad/66_civilian_security_quest_board.md")
QUEST_ROW = re.compile(r"\|\s*([^|]+?)\s*\|\s*([FEDCBAS])\s*\|.*?\|\s*([\d,]+)G")


def check_quest_ranks() -> int:
    """依頼票の基準額が、そのランクの報酬帯に収まっているか。

    **依頼ランクは「その依頼を安全に完遂するための総合難度」**であって、場所の
    推奨レベルとは別物である(`world/06_economy.md`)。だから場所のLv帯と依頼ランクが
    一段ずれること自体は正しい。**ずれてはいけないのは、ランクと基準額の方**である。
    ここが合っていれば、ランクは少なくとも報酬制度と矛盾していない。
    """
    bad, total = [], 0
    for rel in QUEST_BOARDS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        section = ""
        for line in open(path, encoding="utf-8"):
            if line.startswith("## "):
                section = line.strip("# \n")
            m = QUEST_ROW.match(line)
            if not m:
                continue
            total += 1
            name, rank, amount = m.group(1), m.group(2), int(m.group(3).replace(",", ""))
            lo, hi = QUEST_BAND[rank]
            if not lo <= amount <= hi:
                bad.append((rel, section, name, rank, amount, lo, hi))
    if not bad:
        print(f"OK: 依頼票の基準額がランク帯に収まっている({total} 件を照合)")
        return 0
    print(f"⚠ ランク帯から外れた依頼 {len(bad)} 件:")
    for rel, section, name, rank, amount, lo, hi in bad:
        print(f"  ✗ {rel} [{section}] {name}"
              f"  {rank}級 {amount:,}G(帯 {lo:,}〜{hi:,})")
    return 1


# 「NPCは〇人」と人手で書いた数。増えるたびに腐るので、書いてあること自体を警告する。
NPC_COUNT = re.compile(r"NPC(?![^。\n]{0,12}ファイル)[^。\n]{0,12}?[0-9０-９]{2,}\s*人")


def check_npc_counts() -> int:
    """NPCの人数を地の文へ書いていないか。

    START_HEREが「主要 NPC は 62 人」のまま取り残されていた。**全角スペースを挟んで
    いたので `[0-9]+人` のgrepをすり抜け、二度の点検を生き延びた。** 人数は増えるたびに
    腐るうえ、複数人ファイル(銀鴉の羽根・ロゼ＆リゼ)があるのでファイル数とも一致しない。

    **書かないのが正解**で、要点は自動生成の`CHARACTERS.md`が持っている。
    """
    hits = []
    for rel in all_md():
        if os.path.basename(rel).startswith(
                ("123_", "DIGEST", "INDEX", "PROGRESS", "CHARACTERS")):
            continue
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                m = NPC_COUNT.search(line)
                # 「10人枠」は現員ではなく、これから埋める予定の数なので腐らない。
                if m and line[m.end():m.end() + 1] != "枠":
                    hits.append((rel, i, m.group(0)))
    if not hits:
        print("OK: NPCの人数を地の文へ書いている箇所なし")
        return 0
    print(f"⚠ NPCの人数が地の文に書かれている {len(hits)} 件(増えるたびに腐る):")
    for rel, i, frag in hits:
        print(f"  ✗ {rel}:{i}  「{frag}」")
    print("   → 数を書かず、`CHARACTERS.md`(自動生成)へ委ねる。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
