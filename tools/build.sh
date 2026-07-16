#!/usr/bin/env bash
# 配布物をまとめて再生成する。
# ファイルを追加・編集したら、これ 1 本で INDEX / 666_all / DIGEST / zip を最新化する。
#
#   bash tools/build.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/4] INDEX.md"
python3 tools/make_index.py

echo "[2/4] 666_all.md (zip 非対応 AI 用の全部載せ)"
python3 tools/make_all.py

echo "[3/4] DIGEST.md (核だけの貼り付け版)"
python3 tools/make_digest.py

echo "[4/4] 666.zip (zip 対応 AI 用。生成物と .git は除外)"
rm -f 666.zip
zip -q -r 666.zip . \
  -x '.git/*' 'tools/*' '666_all.md' 'DIGEST.md' '666.zip'

echo "done. 配布物: 666.zip / 666_all.md / DIGEST.md"
python3 tools/count.py --budget || true
