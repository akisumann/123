#!/usr/bin/env python3
"""INDEX.md を自動生成する。

各 .md ファイルの見出し(H1)と実文字数を集め、ディレクトリごとに一覧化する。
ファイルを追加・削除したら再実行するだけで索引が最新になる。

    python3 tools/make_index.py

AI はこの INDEX.md を「どのファイルに何が書いてあるか」の地図として使い、
場面に必要なファイルだけを開く(= 全部を一度に読まない)。
"""
from __future__ import annotations
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summaries.tsv")

# 索引に載せない(索引自身と、他ファイルの複製である生成物)
SKIP = {"INDEX.md", "DIGEST.md", "666_all.md"}


def load_summaries() -> dict:
    out = {}
    if not os.path.exists(TSV):
        return out
    with open(TSV, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line and "\t" in line:
                p, s = line.split("\t", 1)
                out[p.strip()] = s.strip()
    return out

# ディレクトリ順と日本語ラベル
DIR_ORDER = [
    ("", "リポジトリ直下"),
    ("rules", "rules/ — ゲームルール(判定・戦闘・レベル・スキル・魔法)"),
    ("world", "world/ — 世界観の核(地理・歴史・種族・経済・生成ルール)"),
    ("world/nations", "world/nations/ — 五大国と関連組織"),
    ("world/dragons", "world/dragons/ — 五龍"),
    ("world/crossroad", "world/crossroad/ — クロスロード(主舞台)の全設定"),
    ("characters", "characters/ — キャラクター雛形"),
    ("characters/npcs", "characters/npcs/ — 主要NPC(55人)"),
]


def count_chars(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        return len("".join(f.read().split()))


def first_heading(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()
    return "(見出しなし)"


def rel_dir(rel: str) -> str:
    d = os.path.dirname(rel)
    return d.replace(os.sep, "/")


def main() -> None:
    summaries = load_summaries()
    files = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "tools")]
        for n in fns:
            if not n.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, n), ROOT).replace(os.sep, "/")
            if rel in SKIP:
                continue
            files.setdefault(rel_dir(rel), []).append(rel)

    total = 0
    n_files = 0
    lines = [
        "# INDEX — ファイル索引(自動生成)",
        "",
        "> `python3 tools/make_index.py` で再生成。手で編集しない。",
        "> AI はこの表で「どのファイルに何があるか」を掴み、**場面に必要なファイルだけ**を開く。",
        "> 全ファイルを結合した `_all.md` を丸ごと渡すのは避ける(読み落としの原因)。",
        "",
        "## 読み込みの順番",
        "",
        "1. **必ず最初**: `START_HERE.md`(入口・圧縮版の正典) と `CLAUDE.md`(GM運用ルール)",
        "2. **場面ごと**: 下表から該当ファイルを開く(`CLAUDE.md`「検索プロトコル」に従う)",
        "3. **参照用**: `PROGRESS.md`(作業ログ)は必要時のみ",
        "",
    ]

    for key, label in DIR_ORDER:
        group = sorted(files.get(key, []))
        if not group:
            continue
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| ファイル | 内容(TL;DR) | 文字数 |")
        lines.append("|---|---|---|")
        for rel in group:
            full = os.path.join(ROOT, rel)
            c = count_chars(full)
            total += c
            n_files += 1
            desc = summaries.get(rel) or first_heading(full)
            desc = desc.replace("|", "\\|")
            lines.append(f"| `{rel}` | {desc} | {c:,} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"合計 **{n_files} ファイル / {total:,} 文字**"
                 "(空白除く)。1ファイルずつ読めば、一度に扱う量は常に小さく保てる。")
    lines.append("")

    out = os.path.join(ROOT, "INDEX.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote INDEX.md  ({n_files} files, {total:,} chars)")


if __name__ == "__main__":
    main()
