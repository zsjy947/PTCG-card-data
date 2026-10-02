<!-- 换行语义：本仓库所有数据文件按原始字节存储（.gitattributes `* -text`），
     manifest.json 的 md5 按文件原始字节计算，请勿开启任何换行转换。 -->

# PTCG-card-data

宝可梦集换式卡牌游戏（PTCG）**简中卡表源数据集**：弹索引 + 各弹卡牌元数据 + 数据清单，
由 [PTCG 拆卡模拟器](https://github.com/zsjy947/PTCG-gacha-simulator) 的同步管线每周自动抓取维护。

- **许可**：[CC0 1.0](LICENSE)（本仓库整理者对数据集汇入与格式的权利主张放弃至公共领域）
- **数据来源**：mik.moe（tcg.mik.moe）公开接口，每周自动抓取
- **更新频率**：每周五 UTC 21:00 全量同步，有变化自动提交（`.github/workflows/update-data.yml`）

## Schema（schemaVersion: 1）

数据为源数据原样发布，**不含任何派生字段**。结构版本由 `manifest.json` 的
`schemaVersion` 标识：字段或语义发生结构性变更时递增，并打对应 `v<N>` tag；
仅追加新弹/新卡（同结构）不递增。

```
data/
├── cards/<set-id>.json   # 每弹卡表（卡牌条目数组，见下方字段表）
├── sets_index.json       # 弹索引（条目数组：id / code / name / series / seriesZh / count）
├── manifest.json         # 数据清单：schemaVersion / generated（ISO +08:00）/ sets.{id: {count, md5}}
└── waves_151.json        # 收集啦151 官方四弹（旅/望/惊/聚）卡号名单（fetch 管线拆分 151C 用）
```

### cards/<set-id>.json 字段表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `setCode` | string | 弹代码（如 `CSV1C`） |
| `cardIndex` | string | 卡编号（弹内编号） |
| `cardName` | string | 简中卡名 |
| `rarity` | string | 稀有度记号（`C`/`R`/`RR`/`SR`/`●`/`★` 等，源站原样） |

其余字段（英文名、发售日、属相等源站附带元数据）原样保留，不在此逐一列举。
注：**不含卡牌效果文本与卡图**——效果文本与图片由运行时从源站实时获取，不在本数据集内。

### manifest.json 语义

- `sets.<id>.md5`：对应 `cards/<id>.json` 文件**原始字节**的 md5（消费方按 md5 做增量比对，
  只下载与本地不同的弹）；
- `generated`：本次全量同步时间（ISO 8601，+08:00）；
- `151C.json` 为拆分源（保留上游原表），不在 manifest 与弹索引内；
  拆分出的 `151C-LV/WANG/JING/JU.json` 是正式弹。

## 使用

```bash
python fetch_data.py            # 增量同步（已有卡表的弹跳过）
python fetch_data.py --force    # 全量重新同步
python tools/verify_data.py     # 完整性校验（卡数/md5/与上次提交对比）
```

纯 Python 标准库，无第三方依赖。

## 消费方式

- **热更新直链**：`https://cdn.jsdelivr.net/gh/zsjy947/PTCG-card-data@master/data/…`
  与 `https://raw.githubusercontent.com/zsjy947/PTCG-card-data/master/data/…`
- 主仓库 [PTCG-gacha-simulator](https://github.com/zsjy947/PTCG-gacha-simulator) 每周从本仓库
  拉取 `data/` 快照随 exe/APK 发布（其 MIT 许可只覆盖代码，不含本数据集）。

## 署名与免责

- 本数据集由 [PTCG 拆卡模拟器](https://github.com/zsjy947/PTCG-gacha-simulator) 项目
  从 **mik.moe（tcg.mik.moe）公开接口**每周自动抓取整理；数据内容的权利归原作者与
  来源站所有，本仓库的 CC0 许可仅覆盖本仓库自身的整理与格式工作，不含上游内容
  （卡文/卡图/商标）的任何权利。
- 本数据集**不含**卡牌效果文本与卡图；图片与详情文本需运行时从来源站获取。
- 本项目仅供学习交流，与官方无任何关联。宝可梦（Pokémon）及相关名称为
  Nintendo / Creatures / GAME FREAK / The Pokémon Company 的商标。
