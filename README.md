# 666 — ファンタジーTRPG世界「クロスロード」設定リポジトリ

TRPG 世界「666」の設定データベース兼・正典（137 ファイル / 約 42 万文字）。
AI にセッションを回してもらうための資料集です。

## AI に読ませるとき

**`_all.md`（全結合・42 万文字）を丸ごと渡さないでください。** 量が多すぎて途中が
読み飛ばされます。代わりに、次の入口から始めます。

| 目的 | 渡すもの |
|---|---|
| 最初に必ず | **[`START_HERE.md`](START_HERE.md)**（入口＋圧縮版の正典）＋ `CLAUDE.md` |
| どのファイルに何があるか | **[`INDEX.md`](INDEX.md)**（全ファイルの地図） |
| 検索できない AI に貼る | **`DIGEST.md`**（上記をまとめた小さい版） |
| 各場面の詳細 | `INDEX.md` を見て、その場面に必要なファイルだけ追加で渡す |

考え方の詳細は `START_HERE.md` の冒頭を参照。

## メンテナンス用ツール

```bash
python3 tools/make_index.py    # INDEX.md を再生成（ファイルを追加/削除したら実行）
python3 tools/make_digest.py   # DIGEST.md を再生成
python3 tools/count.py --budget # 文字数を計測、入口の肥大を警告
```

## ディレクトリ

- `world/` … 世界観（地理・歴史・種族・経済・生成ルール）／`nations/` 五大国／`dragons/` 五龍／`crossroad/` 主舞台クロスロード
- `characters/npcs/` … 主要 NPC 55 人（通り名一覧は `world/crossroad/44_crossroad_nicknames.md`）
- `rules/` … 判定・戦闘・レベル・スキル・魔法
- `CLAUDE.md` … GM 運用ルール（検索プロトコル等）
- `PROGRESS.md` … 作業ログ
