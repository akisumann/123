# 123 ツール一式(機械側)

> **TL;DR:** 設定データ(canon)とは別の、街を機械的に動かす側。配置・掲示板・噂・戦闘判定・整合チェックの各ツールと、その入力データ。

このフォルダは、世界設定そのもの(`world/`・`characters/`・`rules/`)とは役割が違う。
**AIが記憶や雰囲気で決めてしまう部分を、コードに肩代わりさせるための道具**をまとめてある。

- 誰がどこにいるか → 生活ルーティン＋固定乱数で決める(AIが都合で人を選ばない)
- どんな依頼が出ているか → 既存の依頼表から引く(その場で考えない・相場を外さない)
- 何が噂されているか → 実際に起きたことから拾う(思いつきで作らない)
- 戦闘の出目 → 実際に振る(数字を後から都合よく作れない)
- 新キャラの数値 → 計算で出す(レベルとの整合が崩れない)

Python 3 だけで動く(外部ライブラリ不要)。**リポジトリのルートから**実行する。

---

## 進行中に使う(この順に通す)

### 1. その日の街を出す

```bash
python3 tools/day_brief.py                 # 今日ぶん(暦・天候・行事・配置・掲示板・噂)
python3 tools/day_brief.py --time 宵       # その刻だけ
python3 tools/day_brief.py --json          # JSONで出す(Pythonを実行できないAIへ渡す用)
```

内訳を個別に見たい時:

```bash
python3 tools/day_plan.py --time 宵        # 配置だけ(店・施設まで)
python3 tools/day_plan.py --place 東区     # その区画だけ
python3 tools/day_plan.py --who ミルカ     # 一人の一日を追う
python3 tools/quest_board.py               # ギルドの依頼板
python3 tools/quest_board.py --district 東区  # 区画の街区掲示板(軽い仕事・告知)
python3 tools/street_talk.py --place 東区  # その区画に届いている噂
```

### 1.5 誰が何者かを掴む

`CHARACTERS.md`(自動生成の名簿)に60人の要点が1枚でまとまっている。まずここで当たりを付け、
描写する人物だけ次の`scene_context.py`へ降りる。生成は`python3 tools/make_roster.py`(build.shに同梱)。

### 2. 場面に出す人物の情報を引く

```bash
python3 tools/scene_context.py --chars 天雷,ツバキ --place 夜鴉の止まり木 --time 宵
```

ステータス・スキル・口調・行きつけ・よく接する人物・その店の常連を1ブロックで出す。
**これを読んでから描写する。** 記憶で書かない。

### 3. 戦闘

```bash
python3 tools/battle_roll.py --enemy 大型魔物 \
  --act 天雷:超遠隔照準:DEX --act ツバキ:鎖鎌術:DEX --mob Lv30x3 --bonus 天雷:+5:高所からの狙撃
python3 tools/battle_roll.py --who 天雷    # その人のステータス・スキル・ダイス面数
```

`スキルLv d ステータスランク`(S=d7〜F=d1)を実際に振り、出目を一つずつ出す。

### 3.4 巡穣祭の料理大会

```bash
python3 tools/cook_off.py                 # 今日の月の大会(出場者・腕前・順位)
python3 tools/cook_off.py --crop 芋       # 主役作物を指定する
```

**出場者も腕前も乱数。** 街に「料理の腕」という格付けは無いので、**結果を`characters/`へ
書き戻さない。** 毎回振り直す前提で回す(`world/crossroad/47_crossroad_harvest_festival.md`)。

### 3.5 カジノ(魔導盤レース)

```bash
python3 tools/casino_race.py --day 93 --race 3          # 出走表(客が見る情報だけ)
python3 tools/casino_race.py --day 93 --race 3 --run    # 本番を走らせる
python3 tools/casino_race.py --day 93 --race 3 --run --reveal   # 脚質も見る(GM専用)
```

**倍率を決めてから1着を引かない。** 何千回も試走して勝率を出し、そこから倍率を付ける。
**脚質(区画ごとの得手不得手)は非公開で倍率に載らない**ので、盤を長く見ている常連だけが
歪みを取れる。作中の人物に脚質を言葉で説明させないこと。

### 4. 日を進める

```bash
python3 tools/day_plan.py --advance        # 1日進める(--advance 7 で7日)
```

作中の日付は `tools/session_day.txt` の1行だけ。状態として持っているのはこの整数のみで、
配置も天候も掲示板も噂も、すべてこの日付から計算される(同じ日付なら何度引いても同じ結果)。

---

## 世界を編集する時に使う

```bash
python3 tools/generate_character_stats.py --level 40 --stats ATK,DEX,SPD,HP,DEF,MP,INT
python3 tools/check_character_stats.py     # 全キャラのレベルとステータス・スキル合計を検算
bash tools/build.sh                        # 配布物を再生成(TL;DR挿入・索引・全部載せ・JSON・zip)
python3 tools/day_plan.py --check          # ルーティン表の整合確認
```

新キャラの数値はAIが決めず、`generate_character_stats.py`が出したものを貼る
(`rules/10_new_character_format.md`)。

---

## 入力データ

| ファイル | 中身 |
|---|---|
| `routines.tsv` | 住人60人の生活ルーティン。行動型(不動/定住/遊動)・注目度・同行・追従・遠出率・時間帯ごとの区画の重み |
| `session_day.txt` | 作中の今日が何日目か(1行) |
| `summaries.tsv` | 各ファイルのTL;DR。`apply_summaries.py`が本文へ挿入する |

`routines.tsv` 以外の対応関係は、**canonのファイルから直接読む**(専用の対応表を作らない)。

- 施設・行きつけ・宿 → `world/crossroad/72_place_character_map.md`(`venue_map.py`が抽出)
- 依頼の掲示例 → `world/crossroad/64・65・66`、街区掲示板は `22`
- 暦・天候・行事 → `world/70_calendar_and_climate.md`
- ステータス・スキル → `characters/npcs/`
- 知人関係 → 各NPCファイルの「よく接する人物」

canonを直せばツールの出力も変わる。二重管理にならないための方針である。

---

## ファイル一覧

| ツール | 役割 |
|---|---|
| `day_brief.py` | その日の街を一枚に(他ツールをまとめて呼ぶ / `--json`) |
| `day_plan.py` | 配置生成。暦・天候・行事・遠出(泊まりがけ)・めぐり合わせ。日付の管理も |
| `venue_map.py` | 72から施設×人物を抽出(区画の中のどの店にいるかを決める) |
| `quest_board.py` | ギルドの依頼板／区画の街区掲示板 |
| `street_talk.py` | 噂の発生と伝播(悪天候で伝達が遅れる) |
| `scene_context.py` | 場面に必要なcanonを1ブロックに抽出／`--edit`で編集前の全文と注意点 |
| `battle_roll.py` | 戦闘ダイスを実際に振る |
| `casino_race.py` | 魔導盤レースの出走表・倍率・本番を処理する |
| `cook_off.py` | 巡穣祭の料理大会(出場者・腕前を乱数で引く。結果は設定にしない) |
| `make_place_map.py` | 72の「行きつけの店」を49から生成する(手書きしない) |
| `generate_character_stats.py` / `check_character_stats.py` | 新キャラの数値生成・検算(ステータス合計・スキル合計・冒険者ランク・SS誤用) |
| `vetting_report.py` | 未検分レポート(インポート当時のまま手が入っていないファイルの洗い出し) |
| `make_roster.py` | NPC名簿`CHARACTERS.md`を生成 |
| `build.sh` | 配布物の再生成(以下をまとめて実行) |
| `apply_summaries.py` / `make_index.py` / `make_all.py` / `make_digest.py` / `make_json.py` / `count.py` | 索引・全部載せ・ダイジェスト・JSON・文字数 |
| `check_links.py` | リンク整合＋**行きつけと常連の食い違い**＋**「一つしかない物」の重複**を検査 |

編集時は`scene_context.py --edit <名前>`、未検分の確認は`vetting_report.py`。
どちらも「読まずに書く」「ユーザーが目を通していない記述を指示より優先する」を防ぐためのもの。
