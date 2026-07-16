# INDEX — ファイル索引(自動生成)

> `python3 tools/make_index.py` で再生成。手で編集しない。
> AI はこの表で「どのファイルに何があるか」を掴み、**場面に必要なファイルだけ**を開く。
> 全ファイルを結合した `_all.md` を丸ごと渡すのは避ける(読み落としの原因)。

## 読み込みの順番

1. **必ず最初**: `START_HERE.md`(入口・圧縮版の正典) と `CLAUDE.md`(GM運用ルール)
2. **場面ごと**: 下表から該当ファイルを開く(`CLAUDE.md`「検索プロトコル」に従う)
3. **参照用**: `PROGRESS.md`(作業ログ)は必要時のみ

## リポジトリ直下

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `CLAUDE.md` | 666 — ファンタジーTRPG世界構築リポジトリ | 8,824 |
| `PROGRESS.md` | PROGRESS | 16,224 |
| `README.md` | 666 — ファンタジーTRPG世界「クロスロード」設定リポジトリ | 836 |
| `START_HERE.md` | はじめに読む（START HERE）— AI 向け入口 | 3,053 |

## rules/ — ゲームルール(判定・戦闘・レベル・スキル・魔法)

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `rules/00_level_system.md` | レベルシステム | 1,492 |
| `rules/01_skill_system.md` | スキルシステム | 1,265 |
| `rules/02_status_system.md` | ステータスシステム | 1,124 |
| `rules/03_combat_system.md` | 判定・戦闘システム | 1,897 |
| `rules/05_magic_theory.md` | 魔法階位理論 | 6,671 |
| `rules/06_personality_conversion.md` | ステータス・スキル → 性格/コミュ力 変換フォーマット | 1,941 |
| `rules/10_new_character_format.md` | 新規キャラクター生成フォーマット | 2,944 |
| `rules/11_colosseum_duel_system.md` | コロッセオ用・3ターン公開模擬決闘ルール | 3,204 |

## world/ — 世界観の核(地理・歴史・種族・経済・生成ルール)

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `world/00_core_concept.md` | 世界の核設定 | 643 |
| `world/01_geography.md` | 地理概要 | 889 |
| `world/02_alvein_continent.md` | アルヴェイン大陸 | 2,784 |
| `world/03_history.md` | 歴史年表 | 876 |
| `world/04_monster_taxonomy.md` | モンスター分類 | 1,718 |
| `world/05_civilization_classification.md` | 文明人分類 | 1,086 |
| `world/06_economy.md` | 経済・通貨システム | 7,283 |
| `world/07_settlement_generation.md` | 集落・都市生成ルール | 480 |
| `world/08_danger_zone_generation.md` | 危険地域生成ルール | 1,998 |
| `world/09_dungeon_generation.md` | ダンジョン生成ルール | 1,328 |
| `world/10_road_generation.md` | 街道生成ルール | 1,139 |
| `world/12_mermaid.md` | 人魚 | 1,034 |
| `world/13_giant.md` | 巨人 | 1,151 |
| `world/14_adventurers_guild.md` | 冒険者ギルド | 3,372 |
| `world/16_minor_nations.md` | セントラル・ヘイヴン王国周辺の小国 | 1,142 |
| `world/26_amamiya.md` | 雨宮(あまみや) | 1,985 |

## world/nations/ — 五大国と関連組織

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `world/nations/15_central_haven_kingdom.md` | セントラル・ヘイヴン王国 | 1,017 |
| `world/nations/17_central_haven_undead_problem.md` | セントラル・ヘイヴン王国の課題：大地龍の生命力 | 2,693 |
| `world/nations/18_religious_organizations.md` | セントラル・ヘイヴン王国の宗教組織 | 2,135 |
| `world/nations/19_twin_hammer_order.md` | 双槌の聖戦修道女団 | 8,631 |
| `world/nations/23_volcanic_forge_empire.md` | ヴォルカニック・フォージ帝国 | 3,934 |
| `world/nations/24_crystal_frost_empire.md` | クリスタル・フロスト帝国 | 2,608 |
| `world/nations/25_aqua_flow_union.md` | アクア・フロウ連合 | 5,807 |
| `world/nations/34_eternal_grove_kingdom.md` | エターナル・グローブ王国 | 1,498 |
| `world/nations/35_eternal_grove_marukago_formation.md` | 丸籠陣形(まるかごじんけい) | 5,407 |

## world/dragons/ — 五龍

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `world/dragons/36_forest_five_dragons.md` | 森林五枝竜 | 748 |
| `world/dragons/37_earth_dragon.md` | Lv95 大地龍 | 1,017 |
| `world/dragons/38_volcano_dragon.md` | Lv97 火山龍 | 863 |
| `world/dragons/39_ice_dragon.md` | Lv93 氷結龍 | 1,142 |
| `world/dragons/40_ocean_dragon.md` | Lv96 海洋龍 | 959 |
| `world/dragons/41_forest_dragon.md` | Lv94 森林龍 | 1,281 |

## world/crossroad/ — クロスロード(主舞台)の全設定

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `world/crossroad/11_crossroad_city.md` | クロスロード | 18,458 |
| `world/crossroad/20_crossroad_city_districts.md` | クロスロード市内区画設定 | 14,690 |
| `world/crossroad/21_crossroad_inns.md` | クロスロード冒険者向け宿・5種 | 2,660 |
| `world/crossroad/22_crossroad_bulletin_boards.md` | クロスロードの掲示板 | 671 |
| `world/crossroad/27_crossroad_colosseum.md` | クロスロード・コロッセオ | 4,624 |
| `world/crossroad/28_crossroad_casino.md` | クロスロード・カジノ | 2,805 |
| `world/crossroad/29_crossroad_magic_board_race.md` | 魔導盤レース | 3,969 |
| `world/crossroad/30_crossroad_purification_institute.md` | クロスロード浄化院 | 2,147 |
| `world/crossroad/31_crossroad_security_forces.md` | クロスロードの治安組織 | 1,434 |
| `world/crossroad/32_black_needle_society.md` | 黒針会(こくしんかい) | 9,750 |
| `world/crossroad/33_crossroad_magic_slot.md` | 魔導スロット | 1,460 |
| `world/crossroad/42_crossroad_artisan_goods.md` | クロスロード職人区・冒険者向け商品 | 3,871 |
| `world/crossroad/43_crossroad_magic_circle.md` | クロスロード民間魔法サークル(クロスロード民間術師会) | 5,322 |
| `world/crossroad/44_crossroad_nicknames.md` | クロスロード住民の通り名一覧 | 4,503 |
| `world/crossroad/45_crossroad_district_markets.md` | クロスロード各区画の市場 | 4,059 |
| `world/crossroad/46_crossroad_matchmaking_festival.md` | 結び路の祝祭(通称:婚活祭り) | 4,216 |
| `world/crossroad/47_crossroad_harvest_festival.md` | 巡穣祭(通称:○○祭り) | 3,893 |
| `world/crossroad/48_grand_temple_dragon_records.md` | 中央区大神殿 | 4,196 |
| `world/crossroad/49_crossroad_dining.md` | クロスロードの酒場・茶屋・高級料理店 | 2,092 |
| `world/crossroad/50_crossroad_brothels.md` | 西区の主要娼館 | 2,466 |
| `world/crossroad/51_black_needle_info_network.md` | 黒針会情報屋網 | 5,416 |
| `world/crossroad/52_crossroad_gates_streets.md` | クロスロードの門と大通り | 1,690 |
| `world/crossroad/53_crossroad_wandering_events.md` | クロスロード散策イベント | 1,564 |
| `world/crossroad/54_crossroad_theater.md` | クロスロード大劇場《万象座》と巡業劇団 | 3,537 |
| `world/crossroad/55_crossroad_bathhouse.md` | クロスロード東区公衆浴場《四路の湯》 | 3,500 |
| `world/crossroad/56_crossroad_gadget_workshop.md` | クロスロード南区・特殊機構工房《仕掛屋・六番工房》 | 4,469 |
| `world/crossroad/57_black_glass_ruins.md` | 黒硝子遺跡 | 4,209 |
| `world/crossroad/58_forgotten_mine.md` | 忘れられた鉱山 | 4,171 |
| `world/crossroad/59_star_devourer_temple.md` | 星喰いの地下神殿 | 4,458 |
| `world/crossroad/60_sazameki_plains.md` | さざめき平原 | 2,747 |
| `world/crossroad/61_red_fang_forest.md` | 赤牙森林 | 3,847 |
| `world/crossroad/62_grey_rock_canyon.md` | 灰岩峡谷 | 4,893 |
| `world/crossroad/63_bone_toll_moor.md` | 骨鳴り墓原 | 5,490 |
| `world/crossroad/64_danger_zone_quest_board.md` | クロスロード周辺・冒険者ギルド依頼表 | 3,707 |
| `world/crossroad/65_dungeon_quest_board.md` | クロスロード周辺・ダンジョン依頼表 | 4,178 |
| `world/crossroad/66_civilian_security_quest_board.md` | クロスロード周辺・護衛と治安の依頼表 | 2,898 |
| `world/crossroad/67_crossroad_casino_high_and_low.md` | ハイアンドロー | 2,135 |
| `world/crossroad/68_crossroad_casino_war.md` | カジノウォー | 1,441 |
| `world/crossroad/69_crossroad_seven_indian_poker.md` | セブンインディアンポーカー | 1,675 |

## characters/ — キャラクター雛形

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `characters/_template.md` | キャラクターシート雛形 | 518 |

## characters/npcs/ — 主要NPC(55人)

| ファイル | 内容(見出し) | 文字数 |
|---|---|---|
| `characters/npcs/01_clarisse_weissfeld.md` | クラリス・ヴァイスフェルト | 4,478 |
| `characters/npcs/02_milene_weissfeld.md` | ミレーヌ・ヴァイスフェルト | 4,090 |
| `characters/npcs/03_valeria_grenz.md` | ヴァレリア・グレンツ | 2,899 |
| `characters/npcs/04_ada_lockwell.md` | エイダ・ロックウェル | 1,883 |
| `characters/npcs/05_luca_fennel.md` | ルカ・フェンネル | 1,511 |
| `characters/npcs/06_galm_forgelight.md` | ガルム・フォージライト | 2,152 |
| `characters/npcs/07_dario_langford.md` | ダリオ・ラングフォード | 3,517 |
| `characters/npcs/08_silver_raven_feather.md` | 女性冒険者チーム：銀鴉の羽根 | 4,087 |
| `characters/npcs/09_celia.md` | セリア | 1,339 |
| `characters/npcs/10_linette.md` | リネット | 1,760 |
| `characters/npcs/11_marina.md` | マリナ | 1,381 |
| `characters/npcs/12_roze_and_rize.md` | 盗人姉妹：ロゼとリゼ | 2,417 |
| `characters/npcs/13_mika.md` | ミルカ | 2,114 |
| `characters/npcs/14_mina.md` | ミーナ | 2,439 |
| `characters/npcs/15_zara.md` | ザラ | 2,810 |
| `characters/npcs/16_gideon.md` | ギデオン | 3,365 |
| `characters/npcs/17_riera.md` | リエラ | 1,101 |
| `characters/npcs/18_milei.md` | ミレイ | 2,242 |
| `characters/npcs/19_rosalia.md` | ロザリア | 1,508 |
| `characters/npcs/20_bernadette.md` | ベルナデッタ | 2,411 |
| `characters/npcs/21_elsia.md` | エルシア | 2,931 |
| `characters/npcs/22_balto.md` | バルト | 1,517 |
| `characters/npcs/23_elias_veil.md` | エリアス・ヴェイル | 3,892 |
| `characters/npcs/24_viviana_loudbell.md` | ヴィヴィアナ・ラウドベル | 4,002 |
| `characters/npcs/25_leon_grave.md` | レオン・グレイヴ | 5,515 |
| `characters/npcs/26_serena_gearford.md` | セレナ・ギアフォード | 2,386 |
| `characters/npcs/27_lara.md` | ララ | 5,801 |
| `characters/npcs/28_karla.md` | カーラ | 5,503 |
| `characters/npcs/29_vorgan_gard.md` | ボルガン・ガルド | 4,147 |
| `characters/npcs/30_ultimate_patchwork_iron_kun.md` | アルティメットツギハギアイアンくん | 3,420 |
| `characters/npcs/31_mizushiro.md` | 水城(みずしろ) | 3,040 |
| `characters/npcs/32_souryuu.md` | 蒼龍(そうりゅう) | 1,832 |
| `characters/npcs/33_suiren.md` | 睡蓮(すいれん) | 1,761 |
| `characters/npcs/34_aoba.md` | 青葉(あおば) | 1,695 |
| `characters/npcs/35_himuro.md` | 氷室(ひむろ) | 2,341 |
| `characters/npcs/36_tsubaki.md` | ツバキ | 2,685 |
| `characters/npcs/37_tenrai.md` | 天雷(てんらい) | 2,064 |
| `characters/npcs/38_sayo.md` | 小夜(さよ) | 4,012 |
| `characters/npcs/39_sorasaki.md` | 空咲(そらさき) | 1,805 |
| `characters/npcs/40_awahime.md` | 泡姫(あわひめ) | 2,650 |
| `characters/npcs/41_mamori.md` | マモリ | 2,776 |
| `characters/npcs/42_yuiitsu.md` | 唯一(ゆいいつ) | 1,939 |
| `characters/npcs/43_momiji.md` | 紅葉(もみじ) | 2,045 |
| `characters/npcs/44_kokuu.md` | 黒羽(こくう) | 2,050 |
| `characters/npcs/45_suzuyo.md` | 鈴代(すずよ) | 1,974 |
| `characters/npcs/46_mashiro.md` | 真白(ましろ) | 2,053 |
| `characters/npcs/47_tsurezure.md` | 徒然(つれづれ) | 2,323 |
| `characters/npcs/48_shakuyaku.md` | 芍薬(しゃくやく) | 3,030 |
| `characters/npcs/49_ninrei.md` | 仁礼(にんれい) | 1,988 |
| `characters/npcs/50_kokonoe.md` | 九重(ここのえ) | 1,869 |
| `characters/npcs/51_kusabi.md` | クサビ | 1,864 |
| `characters/npcs/52_kohaku.md` | 琥珀(こはく) | 4,158 |
| `characters/npcs/53_hakkin.md` | 白金(はっきん) | 2,097 |
| `characters/npcs/54_ginsetsu.md` | 銀雪(ぎんせつ) | 2,592 |
| `characters/npcs/55_dakki.md` | 妲己(だっき) | 1,921 |

---

合計 **138 ファイル / 429,134 文字**(空白除く)。1ファイルずつ読めば、一度に扱う量は常に小さく保てる。
