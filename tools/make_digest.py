#!/usr/bin/env python3
"""DIGEST.md を生成する（チャット貼り付け用の小さいまとめ）。

ファイル検索できない AI（ChatGPT 等にテキストを貼るケース）向けに、
「毎回渡す最小セット」だけを 1 ファイルへ結合する。

  含めるもの: START_HERE.md（入口＋圧縮版正典）＋ CLAUDE.md（GM運用ルール）＋ INDEX.md（地図）
  含めないもの: world/ characters/ rules/ の本体（＝場面ごとに INDEX を見て個別に貼る）

これは `_all.md`（42 万文字の全結合）の置き換え。DIGEST は小さいので読み落とされにくい。

  python3 tools/make_digest.py
"""
from __future__ import annotations
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 貼り付け最小セット（この順に結合）
PARTS = ["START_HERE.md", "CLAUDE.md", "INDEX.md"]


def count_chars(text: str) -> int:
    return len("".join(text.split()))


def main() -> None:
    chunks = []
    header = (
        "# DIGEST — 貼り付け用まとめ\n\n"
        "> これは検索できない AI 向けの「毎回渡す最小セット」です。\n"
        "> 各場面の詳細は、INDEX の表を見て該当ファイルだけを追加で貼ってください。\n"
        "> 全 42 万文字の結合版（_all.md）を丸ごと貼らないこと。\n"
    )
    chunks.append(header)
    for rel in PARTS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            body = f.read()
        chunks.append(f"\n\n---\n\n<!-- ===== {rel} ===== -->\n\n{body}")

    out_text = "".join(chunks)
    out = os.path.join(ROOT, "DIGEST.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"wrote DIGEST.md  ({count_chars(out_text):,} chars / 目安 2 万以内なら良好)")


if __name__ == "__main__":
    main()
