#!/usr/bin/env python3
"""各データファイルの見出し直後に 1 行サマリー(TL;DR)を挿入する。

サマリーの元データは tools/summaries.tsv(path<TAB>要約)。
各ファイルの最初の見出し(# …)の直後へ、次の 1 行を差し込む:

    > **TL;DR:** 要約テキスト

冪等: すでに TL;DR 行があれば、tsv の内容で置き換える(重複しない)。
これで、目次や全部載せを読むだけで各ファイルの中身が掴め、AI の「先頭集中読み」が効く。

  python3 tools/apply_summaries.py            # 挿入/更新
  python3 tools/apply_summaries.py --check    # 差分が出るかだけ確認(書き込まない)
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summaries.tsv")
MARK = "> **TL;DR:**"


def load_summaries() -> dict[str, str]:
    out = {}
    with open(TSV, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or "\t" not in line:
                continue
            path, summary = line.split("\t", 1)
            out[path.strip()] = summary.strip()
    return out


def apply_to_file(path: str, summary: str, check: bool) -> bool:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    # 最初の見出し行を探す
    h_idx = None
    for i, l in enumerate(lines):
        if l.lstrip().startswith("#"):
            h_idx = i
            break
    if h_idx is None:
        return False

    new_tldr = f"{MARK} {summary}\n"

    # 見出し直後の空行を飛ばした最初の非空行が既存 TL;DR なら置換
    j = h_idx + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j < len(lines) and lines[j].lstrip().startswith(MARK):
        if lines[j] == new_tldr:
            return False  # 変更なし
        if not check:
            lines[j] = new_tldr
    else:
        # 挿入: 見出し + 空行 + TL;DR + 空行
        block = ["\n", new_tldr]
        if h_idx + 1 < len(lines) and lines[h_idx + 1].strip() != "":
            block.append("\n")
        if not check:
            lines[h_idx + 1:h_idx + 1] = block

    if not check:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    return True


def main() -> None:
    check = "--check" in sys.argv
    summaries = load_summaries()
    changed = 0
    missing = []
    for rel, summary in summaries.items():
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full):
            missing.append(rel)
            continue
        if apply_to_file(full, summary, check):
            changed += 1
    verb = "変更予定" if check else "更新"
    print(f"{verb}: {changed} ファイル / 定義 {len(summaries)} 件")
    if missing:
        print("⚠ tsv にあるが存在しないファイル:")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    main()
