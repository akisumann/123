# 索引（何をいつ AI に渡すか）

> 大量素材を扱うための地図。各ファイルの役割と**ロード層**を一覧化する。
> 層の定義は `ai/loading-strategy.md` を参照。文字数は `python3 tools/count.py` で更新。

## ロード層の早見

- **層1（毎回渡す）**: `world/canon.md`
- **層2（その場面だけ渡す）**: 登場するキャラ / 場所 / 勢力の詳細
- **層3（基本渡さない・資料庫）**: 全設定・年表・没案など

## ファイル一覧

| ファイル | 役割 | 層 |
|----------|------|----|
| `world/canon.md` | 常時ロードの核（確定事実だけ） | **1** |
| `world/overview.md` | 世界観の要約 | 1〜2 |
| `world/rules.md` | 世界のルール・禁則（最優先） | 1〜2 |
| `world/setting.md` | 舞台・地理・時代 | 2 |
| `world/history.md` | 歴史・年表 | 3 |
| `world/factions.md` | 勢力・組織 | 2 |
| `characters/*.md` | 各キャラ詳細 | 2 |
| `story/premise.md` | プレミス・テーマ | 1〜2 |
| `story/synopsis.md` | あらすじ | 2 |
| `story/arcs.md` | 章構成 | 2〜3 |
| `ai/system-prompt.md` | AI への基本指示 | 1 |
| `ai/style-guide.md` | 語り口 | 1〜2 |
| `ai/loading-strategy.md` | 大量素材の渡し方（この運用の説明） | 参照用 |

## 渡し方のレシピ

- **最小構成（迷ったらこれ）**: `ai/system-prompt.md` + `world/canon.md`
- **1 シーン回す**: 上記 + そのシーンに出る層2ファイルだけ
- **設定を作り込む相談**: 該当ファイルだけを開いて個別に編集（全部は渡さない）
