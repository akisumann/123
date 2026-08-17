# INDEX — ファイル索引(自動生成)

> `python3 tools/make_index.py`(または `bash tools/build.sh`)で再生成。手で編集しない。
> AI はこの表で「どのファイルに何があるか」を掴み、**場面に必要なファイルだけ**を開く。
> 渡し方は AI の能力次第(zip＞全部載せ 123_all.md＞DIGEST)。詳細は `START_HERE.md`。

## 読み込みの順番

1. **必ず最初**: `START_HERE.md`(入口・圧縮版の正典) と `CLAUDE.md`(GM運用ルール)
2. **場面ごと**: 下表から該当ファイルを開く(`CLAUDE.md`「検索プロトコル」に従う)
3. **参照用**: `PROGRESS.md`(作業ログ)は必要時のみ

## リポジトリ直下

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `123_city.md` | 123_city — クロスロード編(単一ファイル版) | 735,705 |
| `CHARACTERS.md` | 主要NPCの要点を1枚に集めた名簿(レベル・拠点区画・得意/不得意・看板スキル・口調・行きつけ)。自動生成。 | 13,060 |
| `CLAUDE.md` | 123 — ファンタジーTRPG世界構築リポジトリ | 9,977 |
| `PROGRESS.md` | PROGRESS | 224,237 |
| `README.md` | 123 — ファンタジーTRPG世界「クロスロード」設定リポジトリ | 1,264 |
| `START_HERE.md` | はじめに読む（START HERE）— AI 向け入口 | 4,035 |

## rules/ — ゲームルール(判定・戦闘・レベル・スキル・魔法)

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `rules/00_level_system.md` | 全生命の実力指標「レベル(1〜100)」の意味と、レベル帯ごとの強さの目安。 | 1,541 |
| `rules/01_skill_system.md` | 技術・才能を表す「スキル」の仕組みとレベル、習得の考え方。 | 1,449 |
| `rules/02_status_system.md` | HP/MP/ATK/DEF/INT/SPD/DEXの7ステータスとランク評価値(S=25〜F=-4)。評価値は段階値(F=−2〜S=5)を符号付きで二乗して導き、7能力の合計を基礎Lv、±2補正で表示Lvとする。 | 1,688 |
| `rules/03_combat_system.md` | HPではなく「戦況値」で進める戦闘判定ルール(スキルLv d ステータスランク)。装備は数字を足さず手札を増やすだけ。決着は戦い切った時点の敵戦況値の残りで見る。敵戦況値は舞台のLv帯で決まり、人数では変わらない。 | 13,321 |
| `rules/05_magic_theory.md` | 第一〜第七階位で構成される魔法の体系と、各階位でできること。 | 8,164 |
| `rules/06_personality_conversion.md` | 戦闘用ステータス・スキルを性格・コミュ力・対人態度へ読み替える補助表。 | 1,987 |
| `rules/10_new_character_format.md` | 新規キャラを作る共通フォーマット(核を一つに絞る・生活面・数値検算)。 | 5,426 |
| `rules/11_colosseum_duel_system.md` | コロッセオ公開試合用の、3ターンで決着する簡易決闘ルール。 | 3,244 |
| `rules/12_pc_creation.md` | 観覧モードからキャラを動かすモードへ移る時の手順。名前と性別を聞き、どんなステータスがいいかを大雑把に聞く。希望が無ければ三タイプを自動生成して選ばせる。 | 2,788 |
| `rules/13_scene_and_incident.md` | 場面と事件の出し方。出していいのは「その場で終わる日常」か「依頼票に書ける事件」だけで、意味ありげな予兆を置かない。出す物が無い時はその場で作らず、種(75)・掲示例(64〜66)・散策(53)から引く。各所のGM運用の禁止事項を集約。 | 2,753 |

## world/ — 世界観の核(地理・歴史・種族・経済・生成ルール)

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `world/00_core_concept.md` | 世界の根本設定。強さ=レベル+ステータス+スキル、継続拡張が前提。 | 687 |
| `world/01_geography.md` | 惑星規模の地理概要。複数大陸と無数の島々が存在する。 | 926 |
| `world/02_alvein_continent.md` | 主舞台アルヴェイン大陸の概要。五地域・五大国を擁する有数の文明圏。 | 2,828 |
| `world/03_history.md` | 神代(五龍到来)→開拓→国家成立→戦乱→現在、の歴史年表。 | 916 |
| `world/04_monster_taxonomy.md` | モンスターの基本種族分類(非網羅的な管理用リスト)。 | 1,755 |
| `world/05_civilization_classification.md` | 知性ある存在を文明圏との関係で分ける「文明人分類」。 | 1,123 |
| `world/06_economy.md` | 通貨G・物価・冒険者ランク別報酬・素材買い取りランク制度。金額を動かす場面の基準。 | 9,044 |
| `world/07_settlement_generation.md` | 集落・都市を規模に応じて生成するルール(付随する危険地域等)。 | 522 |
| `world/08_danger_zone_generation.md` | 魔物・魔力で危険化した「危険地域」を生成するルール。 | 2,185 |
| `world/09_dungeon_generation.md` | 自然発生・遺構・人工など、ダンジョンを生成するルール。どのダンジョンにもコアがあり(作り出すクリエイトコア／忘れさせるオブリビオンコア／操るパペッターコア／大きくするマグニファイコア)、壊すと止まるので収支の面で壊さない。半起動という状態もある。 | 3,678 |
| `world/10_road_generation.md` | 集落を結ぶ街道の生成ルールと、街道から外れるほど上がる危険度。 | 1,181 |
| `world/12_mermaid.md` | 海洋種族「人魚」。アクア・フロウ連合の主要種族。 | 1,069 |
| `world/13_giant.md` | 極寒適応の大型種族「巨人」。クリスタル・フロスト帝国の主要種族。 | 1,194 |
| `world/14_adventurers_guild.md` | 世界最大の中立組織・冒険者ギルド。依頼の流れ・F〜Sランク制度・素材買取。 | 5,214 |
| `world/16_minor_nations.md` | セントラル・ヘイヴン王国周辺に点在する多数の小国。 | 1,178 |
| `world/26_amamiya.md` | 統制パーティー4人が水の身体を融合させた合体形態「雨宮(水精女王)」。 | 2,412 |
| `world/27_ginsetsu_soukaku_mamori.md` | マモリが銀雪を着ただけの姿・銀雪装殻(Lv65)。それだけで十字剣クロスブレードが振れてしまう。 | 5,220 |
| `world/28_perfect_kohaku.md` | 琥珀が深夜テンションで完成させた全高3mの複合錬金ロボ・パーフェクト琥珀(Lv65)。本来は全パラA級の万能兵器だったが、「見てもらわねば意味がない」で胴体正面に本人がむき出しで乗る構造へ変更した結果、HP:F・DEF:Fのまま。乗ると頭と手先が下がり、一番大きい一手は乗らない方が大きい。それでも本人は「最高にカッコいい!」と大満足。現在は廃研究施設の倉庫の肥やし。 | 3,381 |
| `world/70_calendar_and_climate.md` | クロスロードの暦(1年12ヶ月×30日×三旬)・時間帯・季節(大地龍で薄い四季)・天候の共通枠組みと年中行事の位置づけ。 | 4,141 |

## world/nations/ — 五大国と関連組織

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `world/nations/15_central_haven_kingdom.md` | 五大国の一つ、クロスロードを擁するセントラル・ヘイヴン王国(農業・商業国家)。 | 1,067 |
| `world/nations/17_central_haven_undead_problem.md` | 大地龍の生命力残滓が招く、王国のアンデッド発生問題。 | 2,959 |
| `world/nations/18_religious_organizations.md` | 王国の宗教組織群(豊かな土地の恵みと信仰の背景)。 | 2,171 |
| `world/nations/19_twin_hammer_order.md` | 対アンデッド専門で名高い「双槌の聖戦修道女団」。墓原の定期掃討を担う。 | 7,507 |
| `world/nations/23_volcanic_forge_empire.md` | 五大国・ヴォルカニック・フォージ帝国(北西火山地帯、鍛冶・鉱業)。 | 4,202 |
| `world/nations/24_crystal_frost_empire.md` | 五大国・クリスタル・フロスト帝国(北東氷雪地帯、巨人・氷結姫)。 | 2,651 |
| `world/nations/25_aqua_flow_union.md` | 五大国・アクア・フロウ連合(南西海洋地帯、人魚が主要種族)。 | 6,965 |
| `world/nations/34_eternal_grove_kingdom.md` | 五大国・エターナル・グローブ王国(南東森林地帯、精霊樹・森林五枝竜)。 | 1,611 |
| `world/nations/35_eternal_grove_marukago_formation.md` | エターナル・グローブ王国の防衛陣形「丸籠陣形(連結盾)」。 | 5,447 |

## world/dragons/ — 五龍

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `world/dragons/36_forest_five_dragons.md` | 森林龍に連なる五体の守護竜「森林五枝竜」。エターナル・グローブ王国の最高位。 | 1,003 |
| `world/dragons/37_earth_dragon.md` | 五龍の一柱・大地龍(Lv95)。中央平原と生命力の源。 | 1,055 |
| `world/dragons/38_volcano_dragon.md` | 五龍の一柱・火山龍(Lv97)。火山地帯を形作った最強格。 | 903 |
| `world/dragons/39_ice_dragon.md` | 五龍の一柱・氷結龍(Lv93)。氷雪地帯の主。 | 1,604 |
| `world/dragons/40_ocean_dragon.md` | 五龍の一柱・海洋龍(Lv96)。海洋地帯の主。 | 993 |
| `world/dragons/41_forest_dragon.md` | 五龍の一柱・森林龍(Lv94)。巨大森林の主。 | 1,315 |

## world/crossroad/ — クロスロード(主舞台)の全設定

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `world/crossroad/11_crossroad_city.md` | 主舞台クロスロードの総合設定。人口・統治・街の転機・街道・危険地域4/ダンジョン3。 | 17,937 |
| `world/crossroad/20_crossroad_city_districts.md` | 市内5区画(中央/北/東/南/西)の役割・主な施設・主なNPC一覧。 | 18,834 |
| `world/crossroad/21_crossroad_inns.md` | 冒険者向けの宿5軒(安宿〜高級・歓楽街寄り・工房付き)と料金帯。 | 3,112 |
| `world/crossroad/22_crossroad_bulletin_boards.md` | ギルド正式依頼板とは別の、区画ごとの街区掲示板(軽い仕事・求人・告知)。 | 3,875 |
| `world/crossroad/27_crossroad_colosseum.md` | 西区の大型闘技施設。実力抑制リング・賭け・興行試合の運営ルール。 | 5,337 |
| `world/crossroad/28_crossroad_casino.md` | 西区の合法賭博施設。各種ゲームと乱数運用のルール。 | 4,110 |
| `world/crossroad/29_crossroad_magic_board_race.md` | カジノの人気遊戯・魔導盤レース(光の幻獣を走らせるミニ競馬)。系統×地形は公開、四区画の脚は非公開で倍率に載らない。判定は`tools/casino_race.py`。 | 6,760 |
| `world/crossroad/30_crossroad_purification_institute.md` | 中央区の浄化院。土地浄化・呪物処理・結界維持・対アンデッド支援。 | 2,515 |
| `world/crossroad/31_crossroad_security_forces.md` | 衛兵隊・騎士団・ギルド・浄化院の役割分担と衛兵の階級別レベル目安。 | 5,687 |
| `world/crossroad/32_black_needle_society.md` | 街の裏の情報・暗殺組織「黒針会」。会主・幹部・ミレーヌとの関係。 | 7,474 |
| `world/crossroad/33_crossroad_magic_slot.md` | カジノの遊技台・魔導スロット(三本リールの絵柄揃え)。 | 1,691 |
| `world/crossroad/34_crossroad_justice.md` | 捕まえた者が裁かれ牢に入るまで。刑は記録・賠償・労役・出禁・収監・追放、重罪は王都送り。 | 1,431 |
| `world/crossroad/42_crossroad_artisan_goods.md` | 南区職人区で危険地域の素材が加工された、冒険者向け商品の数々。 | 5,235 |
| `world/crossroad/43_crossroad_magic_circle.md` | 街の魔法使いが集う民間魔法サークル(相談・講習・共同作業場)。 | 5,470 |
| `world/crossroad/44_crossroad_nicknames.md` | 主要NPCの通り名・本名・所属の対応一覧(NPC逆引きの起点)。 | 6,040 |
| `world/crossroad/45_crossroad_district_markets.md` | 5区画それぞれ性格の異なる市場(中央広場市・西の夜市・南の投げ売り市等)。 | 9,666 |
| `world/crossroad/46_crossroad_matchmaking_festival.md` | 年一度の婚活祭り「結び路の祝祭」。領主クラリスも強制参加の名物行事。 | 4,462 |
| `world/crossroad/47_crossroad_harvest_festival.md` | 月一度の食の祭り「巡穣祭」。その月最多の作物を街ぐるみで消費。 | 4,676 |
| `world/crossroad/48_grand_temple_dragon_records.md` | 中央区で大地龍を祀る大神殿と、その大地龍石膏像・龍の記録＋他四龍の比較展示。＋台座に差さった大地龍の杖(資格ある者だけが抜ける・誰でも挑戦可・抜いた者へ貸出)。 | 9,736 |
| `world/crossroad/49_crossroad_dining.md` | 区画ごとに客層が棲み分けられた酒場6・茶屋6・高級料理店7軒。各店に常連の顔ぶれを明記し、全NPCがどこかの店で会える「出会いの動線」として運用する。 | 9,239 |
| `world/crossroad/50_crossroad_brothels.md` | 西区の主要娼館三軒《紅玻璃館》《桃灯楼》《百花迷宮》の格と客層。 | 2,399 |
| `world/crossroad/51_black_needle_info_network.md` | 黒針会が運営し生活インフラ化した、伝言・情報屋網の拠点網。 | 5,174 |
| `world/crossroad/52_crossroad_gates_streets.md` | 四街道に対応する四大門と、中央広場へ延びる四本の大通り。 | 1,966 |
| `world/crossroad/53_crossroad_wandering_events.md` | 目的なく街を歩く時に挟む軽い散策イベント(世間話・手伝い・噂話)。 | 1,818 |
| `world/crossroad/54_crossroad_theater.md` | 西区の大劇場《万象座》と巡業劇団(演劇・歌劇・幻術劇)。 | 3,850 |
| `world/crossroad/55_crossroad_bathhouse.md` | 東区の市内最大の公衆浴場《四路の湯》。幅広い住民が集う日常施設。 | 3,366 |
| `world/crossroad/56_crossroad_gadget_workshop.md` | 南区の特殊機構工房《仕掛屋・六番工房》。注文制作・機能付与専門。 | 4,594 |
| `world/crossroad/57_black_glass_ruins.md` | ダンジョン①黒硝子遺跡(全30階)。古代ゴーレム製造施設跡。Lv10〜40。 | 4,773 |
| `world/crossroad/58_forgotten_mine.md` | ダンジョン②忘れられた鉱山(全40階)。空間・記憶異常のある廃鉱山。Lv25〜55。 | 4,777 |
| `world/crossroad/59_star_devourer_temple.md` | ダンジョン③星喰いの地下神殿(第50層まで確認)。宇宙由来を祀る高難度神殿。 | 4,941 |
| `world/crossroad/60_sazameki_plains.md` | 危険地域①さざめき平原(Lv10〜20)。冒険者デビューの定番地。 | 2,983 |
| `world/crossroad/61_red_fang_forest.md` | 危険地域②赤牙森林(Lv25〜35)。薬効資源を守る縄張り持ちの魔獣。 | 4,098 |
| `world/crossroad/62_grey_rock_canyon.md` | 危険地域③灰岩峡谷(Lv40〜50)。飛行魔物と鉱石・結晶の採取地。 | 4,894 |
| `world/crossroad/63_bone_toll_moor.md` | 危険地域④骨鳴り墓原(Lv55〜65)。アンデッドを集める古戦場跡の墓原。 | 6,405 |
| `world/crossroad/64_danger_zone_quest_board.md` | 4つの危険地域を舞台にした、ギルド定番依頼の掲示例。 | 5,109 |
| `world/crossroad/65_dungeon_quest_board.md` | 3つのダンジョンを舞台にした、ギルド定番依頼の掲示例。 | 4,686 |
| `world/crossroad/66_civilian_security_quest_board.md` | 街道・都市が舞台の護衛・盗賊討伐・捕縛・警備の定番依頼例。 | 3,259 |
| `world/crossroad/67_crossroad_casino_high_and_low.md` | カジノのカードゲーム・トゥエルブハイアンドローの遊び方とルール。 | 1,892 |
| `world/crossroad/68_crossroad_casino_war.md` | カジノのカードゲーム・カジノウォーの遊び方とルール。 | 1,077 |
| `world/crossroad/69_crossroad_seven_indian_poker.md` | カジノのカードゲーム・セブンインディアンポーカーのルール。 | 1,908 |
| `world/crossroad/71_crossroad_hospital.md` | 中央区・東区境の総合医院クロスロード大病院。世俗の回復魔法(非教会系)を主軸に日常医療を担い、聖属性・対アンデッドは扱わない。あかりが衛生担当。名前あり4人+モブ職員。診察100〜300G、骨折2,000〜5,000G、入院一日500〜1,000G。市民は補助で半額程度。 | 5,088 |
| `world/crossroad/72_place_character_map.md` | 場所×キャラ対応マップ。区画・施設ごとに常駐/関係NPCを速攻参照できる索引(場所を一つずつ整備中)。 | 9,838 |
| `world/crossroad/73_colosseum_random_pair_tournament.md` | コロッセオが年に数回開く小規模お祭りトーナメント「相棒籤杯(くじ引き二人組)」。街の実力者16人を毎回籤で2人組へ組み直し16→8→4→2で勝ち抜く運用ルール。 | 3,774 |
| `world/crossroad/74_crossroad_training_ground.md` | 西区・コロッセオ隣接の公営稽古場。観客も賭けもなく、有志が自主的に模擬戦・自主練を行う無料開放の広場。判定は通常のrules/03をそのまま使用。 | 2,492 |
| `world/crossroad/75_scenario_seeds.md` | 観覧モードで使える伏線・展開の種のネタ帳(紅葉の星喰いリベンジ、ツバキの決断、ララ・カーラの教え乞い、エルシアの二重生活ニアミス、琥珀の隠しきれなさ、下水道ニート達への細い導線、マモリのファンクラブ、九重・クサビの回復役探し、エリアスの取材癖、レオンのダメと鋭さの落差、黒針会古参の懐古、結び路の祝祭、男女反転薬の流行、下水道の竜の怪談、新人冒険者の大量登録期、娼婦達の客引き合戦、白金の無自覚パワー騒動、銀雪の格納・憑依指南、九重・クサビの大病院凸、墓原の水の巨人の噂、水球の怪物を作った琥珀の師匠、大地龍の杖を抜く余興、みんなでカジノ／コロッセオ／芝居へ行こう、東区の四人が噛み合う、ハイドウェル一軒への大口注文、泡姫が頼む下水道のガラクタ仕分け、歓楽街の大立ち回り、パーフェクト琥珀の自慢話、琥珀の倉庫整理)＋初手から大きい案件の種(黒硝子遺跡のリッチ、赤牙森林の緊急薬効採取、謎の奇病流行、アイアンくん無断起動、双槌の大規模掃討、ボルガン襲撃、都市規模の姉妹喧嘩、ボルガンの鉱山一攫千金作戦、王都から北門へ流れ込む薬)。結末は決めずGMの裁量に委ねる。 | 47,518 |
| `world/crossroad/76_artifacts.md` | 街にある一点物の遺物と作り方、および量産品まで含めた等級表。遺物は所有者へ追加スキルを一つ付与する(Lv7〜8)。最上品質Lv5・良質Lv3・並Lv2と等級が下へ伸びる。 | 14,402 |
| `world/crossroad/77_north_district_trading_houses.md` | 北区大通りに向かい合う二大商会の建物。倉庫を抱える石造りのガルド大商会《金蔵》と、荷が留まらない四つ口のカーウェン商会《空店》、間の通り「商会前」。 | 6,378 |
| `world/crossroad/78_east_district_school.md` | 東区の初等学校《東区第四学校》。生徒120〜150人、教師4〜5人。ララ・カーラが通い織部が教えている。時折、騎士団・鍛冶師・西区の人・冒険者が呼ばれて子供に教える。街全体では約3,000人が学んでいる。 | 3,422 |

## towns/rockwell/ — 鉱山町ロックウェル

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `towns/rockwell/01_rockwell.md` | 灰岩峡谷を越えた先にある鉱山町ロックウェル(街規模・人口2,500)の総合設定。自前の鉱脈で普通に栄えている。街道・峡谷・忘れられた鉱山はクロスロードと共有で、町固有の危険地域は町の先にある。クロスロードとファイルを分ける線引きもここ。 | 1,886 |
| `towns/rockwell/02_rockwell_town.md` | ロックウェルの町の作り。区画ではなく坑口から街道へ下る一本の坂で、上から坑口・選鉱場と精錬所・鍛冶場と住まい・宿と市・荷置き場。坂なので荷方の仕事は上りに集まる。炉は止まらず煙が細ければ何かあった合図。ギルドは出張窓口だけ。 | 1,108 |
| `towns/rockwell/03_rockwell_danger_zones.md` | ロックウェル固有の危険地域。捨石丘陵(Lv10〜20、屑石を積み上げた人工の丘で今も成長中、戦闘より先に地面が敵になる、町の駆け出しの出発点)と雷鳴山地(Lv25〜35、鉱脈が帯電していて金属を持つと狙われる、鉱山町の隣なのに金属を持ち込めない山)。 | 1,670 |
| `towns/rockwell/04_rockwell_mogura_tunnel.md` | ロックウェル固有のダンジョン・大モグラ坑道(全25階、浅層Lv20〜30/中層35〜45/深層50〜60)。入口は人の掘った四角い坑道で奥は獣の丸い穴。四種が別々のやり方で掘り続けるので地図が保たない。中枢のマグニファイコアで個体が大きく肉も濃い。ダンジョン産というだけで栄養価が桁違いで、町は「ダンジョン産でないと物足りない」。奥のものは高級品。 | 5,561 |

## characters/ — キャラクター雛形

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `characters/_template.md` | キャラクターシートの空テンプレート(基本情報・ステータス・スキル・判定)。 | 566 |

## characters/npcs/ — 主要NPC

| ファイル | 内容(TL;DR) | 文字数 |
|---|---|---|
| `characters/npcs/01_clarisse_weissfeld.md` | 領主クラリス。街全体の方針・調整を担う。ミレーヌの実姉。 | 4,765 |
| `characters/npcs/02_milene_weissfeld.md` | 西区・歓楽街組合トップのミレーヌ。黒針会を統制下に。クラリスの実妹。 | 4,897 |
| `characters/npcs/03_valeria_grenz.md` | 領主騎士団長ヴァレリア「特大剣の騎士団長」。街道・都市外防衛のA級。 | 4,504 |
| `characters/npcs/04_ada_lockwell.md` | 衛兵隊長エイダ。都市内の治安責任者。 | 3,594 |
| `characters/npcs/05_luca_fennel.md` | 若手騎士ルカ。冒険者と領主側を繋ぐ現場連絡役。 | 2,594 |
| `characters/npcs/06_galm_forgelight.md` | 南区の腕利き鍛冶師ガルム。武器修理・特注武具の窓口。 | 5,413 |
| `characters/npcs/07_dario_langford.md` | 冒険者ギルド支部長ダリオ。元斥候兼鑑定士で人材鑑定に長ける。 | 4,834 |
| `characters/npcs/08_silver_raven_feather.md` | Bランク女性冒険者4人組「銀鴉の羽根」。街屈指の実力派パーティー。 | 4,586 |
| `characters/npcs/09_celia.md` | 浄化院の若手神官セリア。浄化依頼・軽治療・アンデッド相談の窓口。 | 2,702 |
| `characters/npcs/10_linette.md` | 情報屋リネット。中堅斥候で、有料で依頼の裏事情を教える。 | 3,045 |
| `characters/npcs/11_marina.md` | 東区の世話役マリナ。住民の小さな困りごと・住民依頼の窓口。 | 2,782 |
| `characters/npcs/12_roze_and_rize.md` | 盗人姉妹ロゼ&リゼ。色仕掛けとスリの小悪党、街の軽いトラブル役。 | 4,403 |
| `characters/npcs/13_mika.md` | 南区の薬品職人ミルカ。ヘンテコ薬に紛れて有用な薬も置く掘り出し物店。 | 3,843 |
| `characters/npcs/14_mina.md` | 黒針会幹部「潜入のミーナ」。子供のような外見で潜入・偽装を得意とする。 | 2,818 |
| `characters/npcs/15_zara.md` | 黒針会幹部「蠍尾のザラ」。蠍獣人で暗殺・追跡・裏切り者処理担当のA級。 | 3,377 |
| `characters/npcs/16_gideon.md` | 黒針会会主ギデオン。組織の最終裁定を担う老練な会主。 | 4,132 |
| `characters/npcs/17_riera.md` | ギルド受付リエラ。世話焼きだがかなりの恋愛脳で即カップリング認定。 | 2,419 |
| `characters/npcs/18_milei.md` | 民間魔法サークル取りまとめ役ミレイ。基礎魔法指導・魔法相談の窓口。 | 3,208 |
| `characters/npcs/19_rosalia.md` | 紅玻璃館の筆頭花魁ロザリア。精霊憑依と陰陽循環術を操る。 | 2,322 |
| `characters/npcs/20_bernadette.md` | 桃灯楼の人気嬢ベルナデッタ。犬獣人で広い人脈を持つ緊急招集役。 | 3,317 |
| `characters/npcs/21_elsia.md` | 昼は術師会・夜は百花迷宮の幻術娼婦エルシア。Lv40のレベルキャップ到達者。 | 3,794 |
| `characters/npcs/22_balto.md` | 北門の古参門衛バルト。出入り確認・道案内を担う街の顔役。 | 2,326 |
| `characters/npcs/23_elias_veil.md` | 巡業劇団専属脚本家エリアス・ヴェイル。万象座の代表作を手掛ける。 | 4,547 |
| `characters/npcs/24_viviana_loudbell.md` | コロッセオ専属実況者ヴィヴィアナ。熱狂を作る名物職員。 | 4,531 |
| `characters/npcs/25_leon_grave.md` | カジノの勝負師レオン「灰色の切り札」。勝負に強いが生活能力皆無。 | 4,215 |
| `characters/npcs/26_serena_gearford.md` | 南区・仕掛屋六番工房の店主セレナ。注文制作と機能付与の魔導機構技師。 | 3,276 |
| `characters/npcs/27_lara.md` | 天才児ララ(Lv35)。Lv50到達を境に街を出る計画を立てる。 | 9,456 |
| `characters/npcs/28_karla.md` | ララの相棒カーラ(Lv35)。街を出る計画の同行者。 | 5,841 |
| `characters/npcs/29_vorgan_gard.md` | 北区商業組合長ボルガン・ガルド(Lv48・偽装Lv18)。強欲な大商会会頭。 | 4,867 |
| `characters/npcs/30_ultimate_patchwork_iron_kun.md` | 南区中央広場のツギハギ巨大ゴーレム(起動時Lv59相当)。街の名所。 | 4,118 |
| `characters/npcs/31_mizushiro.md` | 統制パーティー隊長・水城。水精霊。当主・睡蓮に仕える執事兼戦術教官で、蒼龍の姉。 | 5,046 |
| `characters/npcs/32_souryuu.md` | 統制パーティー前衛・蒼龍。水精霊、受け流しの守り手。当主・睡蓮の専属護衛で、水城の妹。 | 3,683 |
| `characters/npcs/33_suiren.md` | 統制パーティー中衛・睡蓮。水精霊、戦場制御役。アクア・フロウの貴族家門の当主で、四人はこの家の一行。 | 3,115 |
| `characters/npcs/34_aoba.md` | 統制パーティー後衛・青葉。水精霊、決定打役。当主・睡蓮の妹で、四人の最年少。 | 2,979 |
| `characters/npcs/35_himuro.md` | コロッセオ専属剣闘士・氷室。アルマジロ獣人の氷装甲住み込み選手。 | 3,210 |
| `characters/npcs/36_tsubaki.md` | 斥候系冒険者ツバキ。ホビットの忍び。 | 4,309 |
| `characters/npcs/37_tenrai.md` | 出稼ぎの弓手・天雷。アマゾネスの一射の名手。 | 2,974 |
| `characters/npcs/38_sayo.md` | 独立のコソ泥・小夜。裏路地を根城にする。 | 4,699 |
| `characters/npcs/39_sorasaki.md` | 独立の空輸便利屋・空咲。飛竜人の運び屋。 | 2,731 |
| `characters/npcs/40_awahime.md` | 下水道の自称管理人・泡姫。ヘドロスライムで浄化・分解を担い衛生を支える。 | 3,634 |
| `characters/npcs/41_mamori.md` | 領主クラリス専属護衛マモリ「双盾」。 | 4,910 |
| `characters/npcs/42_yuiitsu.md` | ソロ冒険者・唯一「横一線」。雑魚討伐の臨時要員。 | 2,888 |
| `characters/npcs/43_momiji.md` | 武者修行中の旅の騎士・紅葉。竜翼人の猪突猛進型。 | 2,973 |
| `characters/npcs/44_kokuu.md` | 紅葉の同行者・黒羽。規律を重んじる天狗の剣士。 | 2,901 |
| `characters/npcs/45_suzuyo.md` | 旅の吟遊詩人・鈴代。人魚で井戸端の噂・情報の担い手。 | 3,117 |
| `characters/npcs/46_mashiro.md` | 下水道のホームレス・真白。アラクネで罠と糸細工の名手、泡姫の親友。 | 2,950 |
| `characters/npcs/47_tsurezure.md` | 下水道仲間・徒然。エルフで精神リンクの使い手。 | 2,933 |
| `characters/npcs/48_shakuyaku.md` | ボルガンお抱えの岩石精霊・芍薬。鉱物鑑定と精製の専門家。 | 3,839 |
| `characters/npcs/49_ninrei.md` | 双槌の聖戦修道女団のベテラン・仁礼。鬼族のシスターで巡回担当。 | 2,877 |
| `characters/npcs/50_kokonoe.md` | 旅の投槍魔導士・九重。クサビの幼馴染。 | 2,818 |
| `characters/npcs/51_kusabi.md` | 旅の巫女・クサビ。結界術の使い手、九重の幼馴染。 | 2,635 |
| `characters/npcs/52_kohaku.md` | 南区の廃研究施設を拠点にする錬金術師・琥珀。ホムンクルス。 | 5,613 |
| `characters/npcs/53_hakkin.md` | 廃研究施設のメイドロボ・白金。怪力の持ち主。 | 3,361 |
| `characters/npcs/54_ginsetsu.md` | 廃研究施設のリビングアーマー・銀雪。ゴースト憑依型の空鎧。 | 4,853 |
| `characters/npcs/55_dakki.md` | 廃研究施設の生体兵装・妲己。巨大肉塊オクトパスの気怠げな存在。 | 3,172 |
| `characters/npcs/56_toyone.md` | 東区に根を張る長命の巨大トレント・豊根。食料・建材・環境を供給し、住民に土地神様と慕われる。 | 4,876 |
| `characters/npcs/57_akari.md` | 中央区・領主邸に常駐する領主家お抱えの浄火精霊・あかり。攻撃性のない炎で浄化・衛生・防疫・照明を担う。 | 4,084 |
| `characters/npcs/58_unabara.md` | クロスロード大病院の感染症・再生医療研究者・海原。人魚。車椅子に担架を連結して疾走・患者搬送も担う。自身の人魚肉に再生効果。 | 4,256 |
| `characters/npcs/59_kazama.md` | クロスロード大病院の外科医・風間。カマイタチの妖怪。大量のメスと鎌鼬の切断力で精密切開、切った端から瞬間治療で閉じる外科の切り札。 | 3,785 |
| `characters/npcs/60_shiromine.md` | クロスロード大病院の院長・白峰。八尺様の妖怪でMP:Sの院内最高の回復術師。大型の治癒砲(ヒールビーム/ヒールキャノン)で重症・集団治療を担う最後の砦。運営は苦手。 | 3,806 |
| `characters/npcs/61_celestina.md` | 西区の臨時護衛セレスティナ。長槍の間合い支配で、娼婦側ではなく場慣れしていない客側につく護衛。伸縮式のテレスコピックスピア(1〜3m)を杖として持ち歩き、スリと絡みを寄せつけない動線管理を売りにする。ホビット・Lv50。 | 7,893 |
| `characters/npcs/62_kasumi.md` | 東区・豊根の幹に住み着いた小型妖精カスミ(身長40cm)。家も食事も豊根で、近所で悪戯をして暮らす。実はLv47・DEX:Sで、味方の見た目偽装・透明化・装備化という街に他の持ち手がいない他者掛け幻覚の使い手だが、行政からは害のない悪戯者としか思われておらずスペックを誰も把握していない。 | 5,511 |
| `characters/npcs/63_asuka.md` | 黒針会「目の幹部」飛鳥。鳥弾視界での広域索敵を交渉材料に使う対外折衝役。狩人パーティーの司令塔。 | 5,024 |
| `characters/npcs/64_raika.md` | 西区の街娼・雷華。雷獣の妖怪で街唯一のSPD:S。人懐っこく元気で、店にも属さず金勘定も分からない。 | 4,984 |
| `characters/npcs/65_rido_carwen.md` | 北区の新興商人リド・カーウェン。カーウェン商会会頭。黒針会に丸ごと担がれているが、ボルガンはそれを織り込んだ上で互角に殴り合っている。 | 7,215 |
| `characters/npcs/66_oribe.md` | 《東区第四学校》の教師・織部。全身を白い霊布で巻いて壁と天井を這う、街の面白名物。昔どこかの小国で退魔師をしていた。布を操る一本だけで積み上げた対策が、そのまま生徒への教材になっている。 | 10,766 |
| `characters/npcs/67_ichika_hidewell.md` | 南区の職人の通り《イチカ防具店》店主。三姉妹の長女イチカ。量産品が中心だが、女性用の鎧は採寸からのオーダーも受ける。 | 4,954 |
| `characters/npcs/68_nino_hidewell.md` | 南区の職人の通り《ニノ弓矢店》店主。三姉妹の次女ニノ。店から動かずマシンガントークで矢を売る。天雷の大弓の調整もこの人。 | 4,070 |
| `characters/npcs/69_san_hidewell.md` | 南区の職人の通り《サン小物店》店主。三姉妹の三女サン。小型ナイフ・針・留め具。手入れの要らない頑丈さで黒針会と斥候に人気。 | 3,635 |

---

合計 **172 ファイル / 1,715,310 文字**(空白除く)。1ファイルずつ読めば、一度に扱う量は常に小さく保てる。
