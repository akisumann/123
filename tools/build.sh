#!/usr/bin/env bash
# 配布物をまとめて再生成する。
# ファイルを追加・編集したら、これ 1 本で INDEX / 123_all / DIGEST / zip を最新化する。
#
#   bash tools/build.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[0/9] 各ファイルへ TL;DR を挿入/更新"
python3 tools/apply_summaries.py

echo "[1/9] CHARACTERS.md (NPC名簿。個別ファイルから生成)"
python3 tools/make_roster.py

echo "[2/9] INDEX.md"
python3 tools/make_index.py

echo "[3/9] 123_all.md (zip 非対応 AI 用の全部載せ)"
python3 tools/make_all.py

echo "[4/9] DIGEST.md (核だけの貼り付け版)"
python3 tools/make_digest.py

echo "[5/9] 123.json (JSON として食えるAI・外部ツール用)"
python3 tools/make_json.py

echo "[6/9] 123.zip (zip 対応 AI 用。生成物と .git は除外)"
rm -f 123.zip
zip -q -r 123.zip . \
  -x '.git/*' 'tools/*' '123_all.md' 'DIGEST.md' '123.zip' '123.json'

echo "[7/9] 123_tools.zip (機械側だけを分けた一式)"
rm -f 123_tools.zip
zip -q -r 123_tools.zip tools -x 'tools/__pycache__/*'

echo "[8/9] リンク整合チェック"
python3 tools/check_links.py || true

echo "done. 配布物: 123.zip(設定) / 123_all.md / 123.json / DIGEST.md / 123_tools.zip(機械側)"
python3 tools/count.py --budget || true
