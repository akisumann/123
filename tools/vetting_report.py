#!/usr/bin/env python3
"""どの記述がまだユーザーの目を通っていないかを、git履歴から洗い出すツール。

このリポジトリは初回に外部AI(GPT)の生成データを一括インポートして作られている。
その後ユーザーとのやり取りで手が入った箇所と、**インポート当時のまま残っている箇所**が
混在しており、後者を「canonだから」と信じて扱うと、ユーザー本人が知らない設定を
根拠に判断してしまう(実例:睡蓮の「戦況を語る時だけ饒舌」)。

TL;DR一括挿入やINDEX同期のような全ファイルを機械的に触ったコミットは、内容が
検分された証拠にならないので除外して数える。

    python3 tools/vetting_report.py            # 未検分ファイルの一覧
    python3 tools/vetting_report.py --all      # 全ファイルを編集回数つきで
"""
from __future__ import annotations
import argparse
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 全ファイルを一括で触った機械的なコミット(内容が検分された証拠にならない)
BULK_PATTERNS = (
    "Import 666 world data", "per-file TL;DR", "Full repo tidy-up", "Sync INDEX",
    "Stop tracking", "Rename project codename", "tiered-loading", "all-in-one bundle",
    "TL;DR", "summaries", "行きつけ", "配布物", "loading layer", "storytelling",
)
# 生成物・ログは対象外
SKIP = {"INDEX.md", "DIGEST.md", "PROGRESS.md", "123_all.md"}
SKIP_DIRS = {".git", "tools", "__pycache__"}


def canon_files() -> list[str]:
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md") and fn not in SKIP:
                out.append(os.path.relpath(os.path.join(base, fn), ROOT))
    return sorted(out)


def content_edits(path: str) -> list[str]:
    """そのファイルへの、内容に踏み込んだ編集の履歴。"""
    log = subprocess.run(["git", "log", "--format=%ad %s", "--date=short", "--", path],
                         cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    return [l for l in log if not any(p in l for p in BULK_PATTERNS)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="全ファイルを編集回数つきで出す")
    args = ap.parse_args()

    rows = [(p, content_edits(p)) for p in canon_files()]
    unvetted = [(p, e) for p, e in rows if not e]

    print("=" * 60)
    print("未検分レポート(インポート当時のまま残っている記述の洗い出し)")
    print("=" * 60)
    print(f"\n対象 {len(rows)} ファイル中、**内容に踏み込んだ編集が一度もない**のは "
          f"{len(unvetted)} ファイル。\n"
          "これらは外部AIが生成した文面がそのまま残っている可能性が高く、"
          "ユーザーの意図と食い違っていても誰も気づいていない。")

    if args.all:
        print("\n【全ファイル(内容編集の回数)】")
        for p, e in sorted(rows, key=lambda x: len(x[1])):
            print(f"  {len(e):2d}回  {p}")
    else:
        by_dir: dict[str, list[str]] = {}
        for p, _ in unvetted:
            by_dir.setdefault(os.path.dirname(p) or ".", []).append(os.path.basename(p))
        print("\n【未検分ファイル】")
        for d in sorted(by_dir):
            print(f"\n■ {d}/  ({len(by_dir[d])}件)")
            for f in sorted(by_dir[d]):
                print(f"   {f}")

    print("""
【使い方】
- ここに挙がったファイルの記述は、**ユーザーの指示より優先してはならない**。
  食い違ったらユーザーが正しい(`CLAUDE.md`運用ポリシー、`tools/scene_context.py --edit`)。
- 全部を読み返す必要はない。実際に使う場面が来た時、そのファイルが一覧にあるかを確認し、
  重要な判断の根拠にする前にユーザーへ一言確認する、という使い方でよい。
- 内容に手が入れば、このレポートからは自動的に外れる。""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
