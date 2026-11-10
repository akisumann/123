#!/usr/bin/env python3
"""プレイ記録(play/〈主人公〉.md)を書き換える専用ツール。

GMが場面のたびに文字列を頼りに手で書き換えると、記録が崩れる
(4周目の実例:「この文の後ろに足す」形の追記が、同じ文を持つ手帳の欄へ差し込まれた/
進行が数万字の一段落になった/済んだ約束や使い切った持ち物が残った/残高を暗算で書いた)。
このツールは欄ごとに決まった場所へだけ書き、残高は自分で計算する。**play/ はこれでだけ書き換える。**

欄(この順):
  ## 現在 / ## 所持金 / ## 持ち物 / ## 約束・進行中 / ## 知り合った人 / ## 経過 / ## 〈名〉の手帳

使い方(--file を省くと play/lloyd_game_data.md):
  python3 tools/play_log.py show
  python3 tools/play_log.py now "56日目(1年 二の月 下旬26日)・昼" "南区、茸問屋《湿り蔵》" [--home "東門の外の自分の家"]
  python3 tools/play_log.py log "茸問屋に北東の奥の件を話した" [--when "56日目・昼"]
  python3 tools/play_log.py money -120 "薪(荷車一杯)" [--when "70日目・夕方"]
  python3 tools/play_log.py item 卵 +3 "かみさんにもらった"      # 数の増減。0になったら行を消す
  python3 tools/play_log.py item 薪 --set "荷車一杯" "薪屋から"   # 数でない量は --set
  python3 tools/play_log.py promise add "ツバキが戻ったら穴熊を風下から見に行く"
  python3 tools/play_log.py promise done 3
  python3 tools/play_log.py person 風間 "大病院の外科医。71日目に《水音茶房》で知り合った"
  python3 tools/play_log.py note 56 "(プレイヤーの【メモ】をそのまま。複数行可)"
  python3 tools/play_log.py check

--when を省くと「現在」の日付(括弧の中は落とす)を使う。
"""
from __future__ import annotations
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILE = os.path.join(ROOT, "play", "lloyd_game_data.md")

ORDER = ["現在", "所持金", "持ち物", "約束・進行中", "知り合った人", "経過"]  # 最後に「〜の手帳」
EMPTY = "(なし)"
LONG_LINE = 300  # これより長い行は check で警告(手帳は除く)


# ---------------------------------------------------------------- 読み書き

class Doc:
    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8") as f:
            text = f.read()
        parts = re.split(r"(?m)^## ", text)
        self.head = parts[0]
        self.sections: list[list[str]] = []  # [title, body]
        for p in parts[1:]:
            title, _, body = p.partition("\n")
            self.sections.append([title.strip(), body])

    # 欄の取得(無ければ作る)
    def notebook_title(self) -> str:
        for t, _ in self.sections:
            if t.endswith("の手帳"):
                return t
        raise SystemExit("「〜の手帳」の欄が無い。ファイルを確かめること")

    def get(self, title: str) -> list[str]:
        for s in self.sections:
            if s[0] == title:
                return s
        if title not in ORDER:
            raise SystemExit(f"欄「{title}」が無い")
        # 手帳の直前に作る(順番を保つ)
        sec = [title, f"\n{EMPTY}\n\n"]
        idx = next((i for i, s in enumerate(self.sections) if s[0].endswith("の手帳")), len(self.sections))
        self.sections.insert(idx, sec)
        return sec

    def lines(self, title: str) -> list[str]:
        return self.get(title)[1].strip("\n").split("\n") if self.get(title)[1].strip() else []

    def set_lines(self, title: str, lines: list[str]) -> None:
        body = [l for l in lines]
        if not [l for l in body if l.strip()]:
            body = [EMPTY]
        self.get(title)[1] = "\n" + "\n".join(body).strip("\n") + "\n\n"

    def save(self) -> None:
        out = self.head
        for t, b in self.sections:
            out += f"## {t}\n{b}"
        out = out.rstrip("\n") + "\n"
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(out)


def strip_empty(lines: list[str]) -> list[str]:
    return [l for l in lines if l.strip() and l.strip() != EMPTY]


# ---------------------------------------------------------------- 現在

def current_when(doc: Doc) -> str:
    for l in doc.lines("現在"):
        m = re.match(r"- \*\*日付:\*\*\s*(.+)", l)
        if m:
            when = re.sub(r"[(（][^)）]*[)）]", "", m.group(1))
            return re.sub(r"\s+.*$", "", when.strip()) or when.strip()
    raise SystemExit("「現在」に日付が無い。now で入れること")


def cmd_now(doc: Doc, a) -> str:
    lines = doc.lines("現在")
    def put(key: str, val: str):
        pat = f"- **{key}:**"
        for i, l in enumerate(lines):
            if l.startswith(pat):
                lines[i] = f"{pat} {val}"
                return
        lines.append(f"{pat} {val}")
    put("日付", a.date)
    put("場所", a.place)
    if a.home:
        put("住まい", a.home)
    doc.set_lines("現在", strip_empty(lines))
    return f"現在 → {a.date} / {a.place}"


# ---------------------------------------------------------------- 所持金

def parse_g(s: str) -> int:
    return int(re.sub(r"[^\d-]", "", s.replace("−", "-")))


def fmt_g(n: int) -> str:
    return f"{n:,}G"


def money_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for l in lines:
        if l.startswith("|") and not re.match(r"\|\s*-", l) and "残高" not in l:
            rows.append([c.strip() for c in l.strip("|").split("|")])
    return rows


def cmd_money(doc: Doc, a) -> str:
    lines = doc.lines("所持金")
    rows = money_rows(lines)
    if not rows:
        raise SystemExit("所持金の表が無い")
    bal = parse_g(rows[-1][3])
    delta = parse_g(a.amount)
    new = bal + delta
    if new < 0:
        raise SystemExit(f"残高が足りない({fmt_g(bal)} に {a.amount})")
    when = a.when or current_when(doc)
    sign = "+" if delta > 0 else "−"
    row = f"| {when} | {a.desc} | {sign}{abs(delta):,}G | {fmt_g(new)} |"
    # 表の最後の行の直後に足す
    last = max(i for i, l in enumerate(lines) if l.startswith("|"))
    lines.insert(last + 1, row)
    lines = [f"**{fmt_g(new)}**" if re.fullmatch(r"\*\*[\d,]+G\*\*", l.strip()) else l for l in lines]
    doc.set_lines("所持金", lines)
    return f"所持金 {fmt_g(bal)} → {fmt_g(new)}"


# ---------------------------------------------------------------- 持ち物

def cmd_item(doc: Doc, a) -> str:
    lines = doc.lines("持ち物")
    idx = None
    for i, l in enumerate(lines):
        if l.startswith("|") and [c.strip() for c in l.strip("|").split("|")][0] == a.name:
            idx = i
            break
    note = a.note or ""
    if idx is None:
        if a.set is None and not re.fullmatch(r"\+?\d+", a.delta or ""):
            raise SystemExit(f"持ち物に「{a.name}」が無い。足すなら +数 か --set で")
        count = a.set if a.set is not None else str(int(a.delta))
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, f"| {a.name} | {count} | {note} |")
        doc.set_lines("持ち物", lines)
        return f"持ち物に追加:{a.name} {count}"
    cells = [c.strip() for c in lines[idx].strip("|").split("|")]
    while len(cells) < 3:
        cells.append("")
    if a.set is not None:
        count = a.set
    else:
        if not re.fullmatch(r"\d+", cells[1]):
            raise SystemExit(f"「{a.name}」の数が数字でない({cells[1]})。--set で書き換えること")
        n = int(cells[1]) + int(a.delta)
        if n < 0:
            raise SystemExit(f"「{a.name}」が足りない({cells[1]} に {a.delta})")
        if n == 0:
            del lines[idx]
            doc.set_lines("持ち物", lines)
            return f"持ち物から削除:{a.name}(0になった)"
        count = str(n)
    memo = cells[2]
    if note:
        memo = f"{memo}。{note}" if memo else note
    lines[idx] = f"| {a.name} | {count} | {memo} |"
    doc.set_lines("持ち物", lines)
    return f"持ち物:{a.name} → {count}"


# ---------------------------------------------------------------- 約束・進行中

def cmd_promise(doc: Doc, a) -> str:
    lines = strip_empty(doc.lines("約束・進行中"))
    nums = [int(m.group(1)) for l in lines for m in [re.match(r"- \[(\d+)\]", l)] if m]
    if a.op == "add":
        n = max(nums, default=0) + 1
        lines.append(f"- [{n}] {a.text}")
        msg = f"約束を追加:[{n}]"
    elif a.op in ("done", "edit"):
        key = f"- [{a.text if a.op == 'done' else a.num}]"
        hit = [i for i, l in enumerate(lines) if l.startswith(key + " ")]
        if not hit:
            raise SystemExit(f"約束 {key} が無い")
        if a.op == "done":
            del lines[hit[0]]
            msg = f"約束 {key} を済みにして消した(経過に一行残すこと)"
        else:
            lines[hit[0]] = f"{key} {a.new}"
            msg = f"約束 {key} を書き換えた"
    else:
        raise SystemExit("promise は add / done / edit")
    doc.set_lines("約束・進行中", lines)
    return msg


# ---------------------------------------------------------------- 知り合った人

def cmd_person(doc: Doc, a) -> str:
    lines = strip_empty(doc.lines("知り合った人"))
    if not any(l.startswith("|") for l in lines):
        lines = ["| 名前 | メモ |", "|---|---|"]
    for i, l in enumerate(lines):
        cells = [c.strip() for c in l.strip("|").split("|")]
        if l.startswith("|") and cells[0] == a.name:
            memo = a.memo if a.replace else f"{cells[1]}／{a.memo}"
            lines[i] = f"| {a.name} | {memo} |"
            doc.set_lines("知り合った人", lines)
            return f"知り合った人:{a.name} を更新"
    lines.append(f"| {a.name} | {a.memo} |")
    doc.set_lines("知り合った人", lines)
    return f"知り合った人:{a.name} を追加"


# ---------------------------------------------------------------- 経過

def cmd_log(doc: Doc, a) -> str:
    when = a.when or current_when(doc)
    text = " ".join(a.text.split())
    lines = strip_empty(doc.lines("経過"))
    lines.append(f"- {when}:{text}")
    doc.set_lines("経過", lines)
    warn = f"(長い:{len(text)}字。一場面一行に収めること)" if len(text) > LONG_LINE else ""
    return f"経過に一行:{when}{warn}"


# ---------------------------------------------------------------- 手帳

def cmd_note(doc: Doc, a) -> str:
    title = doc.notebook_title()
    sec = doc.get(title)
    body = strip_empty(sec[1].strip("\n").split("\n"))
    body = [l for l in body if l.strip() != "(まだ何も書いていない)"]
    heading = f"### {a.day}日目"
    entries = []
    for raw in a.text.split("\n"):
        raw = raw.strip()
        if raw:
            entries.append(raw if raw.startswith("- ") else f"- {raw}")
    if heading in body:
        # その日の見出しの塊の末尾に足す
        i = body.index(heading) + 1
        while i < len(body) and not body[i].startswith("### "):
            i += 1
        body[i:i] = entries
    else:
        body += ([""] if body else []) + [heading] + entries
    sec[1] = "\n" + "\n".join(body) + "\n\n"
    return f"手帳の「{heading}」に{len(entries)}行"


# ---------------------------------------------------------------- 表示・点検

def cmd_show(doc: Doc, a) -> str:
    out = []
    for t in ["現在", "約束・進行中"]:
        out.append(f"## {t}\n" + "\n".join(doc.lines(t)))
    rows = money_rows(doc.lines("所持金"))
    out.append(f"## 所持金\n{rows[-1][3] if rows else '?'}")
    log = strip_empty(doc.lines("経過"))
    out.append("## 経過(最後の5行)\n" + "\n".join(log[-5:] or [EMPTY]))
    return "\n\n".join(out)


def cmd_check(doc: Doc, a) -> str:
    problems = []
    titles = [t for t, _ in doc.sections]
    want = ORDER + [doc.notebook_title()]
    if titles != want:
        problems.append(f"欄の並びが違う:{titles}(正しくは {want})")
    # 残高の連鎖
    rows = money_rows(doc.lines("所持金"))
    for prev, cur in zip(rows, rows[1:]):
        try:
            if parse_g(prev[3]) + parse_g(cur[2]) != parse_g(cur[3]):
                problems.append(f"残高が合わない:{cur[0]} {cur[1]}({prev[3]} {cur[2]} → {cur[3]})")
        except (ValueError, IndexError):
            problems.append(f"所持金の行が読めない:{cur}")
    bold = [l for l in doc.lines("所持金") if re.fullmatch(r"\*\*[\d,]+G\*\*", l.strip())]
    if rows and bold and parse_g(bold[0]) != parse_g(rows[-1][3]):
        problems.append(f"太字の残高{bold[0]}が表の最後{rows[-1][3]}と違う")
    # 長すぎる行(手帳は除く)
    for t, b in doc.sections:
        if t.endswith("の手帳"):
            continue
        for l in b.split("\n"):
            if len(l) > LONG_LINE and not l.startswith("|"):
                problems.append(f"「{t}」に長すぎる行({len(l)}字):{l[:40]}…")
    # 約束の書式
    for l in strip_empty(doc.lines("約束・進行中")):
        if not re.match(r"- \[\d+\] ", l):
            problems.append(f"約束の書式が違う:{l[:40]}")
    # 手帳:見出しの外に行が無いか
    nb = strip_empty(doc.get(doc.notebook_title())[1].split("\n"))
    nb = [l for l in nb if l.strip() != "(まだ何も書いていない)"]
    if nb and not nb[0].startswith("### "):
        problems.append("手帳の最初が「### N日目」の見出しになっていない")
    return "点検:問題なし" if not problems else "点検:\n" + "\n".join(f"- {p}" for p in problems)


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=DEFAULT_FILE, help="プレイ記録(既定 play/lloyd_game_data.md)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("show", help="現在・約束・残高・経過の最後を見る")
    sub.add_parser("check", help="欄の並び・残高・長すぎる行・約束と手帳の書式を点検")

    p = sub.add_parser("now", help="現在の日付と場所を書き換える")
    p.add_argument("date"); p.add_argument("place"); p.add_argument("--home")

    p = sub.add_parser("log", help="経過に一場面一行を足す")
    p.add_argument("text"); p.add_argument("--when")

    p = sub.add_parser("money", help="お金を動かす(表に一行・残高は自動)")
    p.add_argument("amount", help="+300 / -120"); p.add_argument("desc"); p.add_argument("--when")

    p = sub.add_parser("item", help="持ち物を増減(0で行を消す)/--setで量を書き換え")
    p.add_argument("name"); p.add_argument("delta", nargs="?", help="+3 / -1")
    p.add_argument("note", nargs="?"); p.add_argument("--set")

    p = sub.add_parser("promise", help="約束・進行中:add 文 / done 番号 / edit 番号 文")
    p.add_argument("op", choices=["add", "done", "edit"]); p.add_argument("text")
    p.add_argument("new", nargs="?")

    p = sub.add_parser("person", help="知り合った人を足す(既にいればメモを継ぎ足す)")
    p.add_argument("name"); p.add_argument("memo"); p.add_argument("--replace", action="store_true")

    p = sub.add_parser("note", help="手帳の「### N日目」の下にプレイヤーのメモをそのまま足す")
    p.add_argument("day"); p.add_argument("text")

    a = ap.parse_args()
    if a.cmd == "item" and a.set is not None and a.delta is not None and a.note is None:
        a.note, a.delta = a.delta, None  # item 名 --set 値 メモ
    if a.cmd == "promise" and a.op == "edit":
        a.num, a.new = a.text, a.new
        if not a.new:
            raise SystemExit("promise edit 番号 新しい文")
    doc = Doc(a.file)
    fn = {"show": cmd_show, "check": cmd_check, "now": cmd_now, "log": cmd_log, "money": cmd_money,
          "item": cmd_item, "promise": cmd_promise, "person": cmd_person, "note": cmd_note}[a.cmd]
    msg = fn(doc, a)
    if a.cmd not in ("show", "check"):
        doc.save()
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
