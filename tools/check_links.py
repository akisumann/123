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
        return 0

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


if __name__ == "__main__":
    raise SystemExit(main())
