# Sheepy A Short Adventure 成就简中汉化

为 **Sheepy: A Short Adventure**（Steam App ID `1568400`，免费游戏）补上 Steam 成就的简体中文。

游戏本体自带官方简中，但成就文本只有英文——官方简中资源里根本不含成就串。本仓库补齐这一块：
30 条成就，名称与描述各 30 条，覆盖率 100%。

> 非官方民间汉化。游戏本体、成就文本与图标的版权归开发者所有，本仓库仅提供本地化的成就文本。

---

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `UserGameStatsSchema_1568400.bin` | **主文件**。含简中成就的 Steam 成就 schema，10 524 字节 |
| `UserGameStatsSchema_1568400.zip` | 标准投稿 ZIP，根目录仅含上面这一个 BIN，可直接导入 SATLI |
| `original/UserGameStatsSchema_1568400.bin` | 未改动的原始 schema（8 601 字节），用于还原 |
| `汉化对照表.md` | 30 条成就的英中对照 + 解锁率 + 逐条译者注 |
| `work/translations.csv` | 译文工作稿，改译文改这里 |
| `work/sources.json` | 研究记录：来源、网络状态、术语依据 |
| `work/report.json` `work/manifest.json` | 构建与校验报告、源文件哈希与覆盖统计 |
| `tools/` | 二进制 KeyValues 编解码器与独立校验脚本，见 [tools/README.md](tools/README.md) |

哈希（SHA-256）：

```
原始 schema   75f1d1f6a337c539e212133dbd6ebf4b10ef318ef4b605ed98828c415ab8a911  (8 601 B)
汉化 schema   c8c88589eb9ecf9b77c3f1201a38eef8e00c25666ac6666da179f1d3570da229  (10 524 B)
投稿 ZIP      bfa1e171da1dd70a360dc8204c601e923d11da5ca0a8dae14bcc0f68e1bfe411
```

---

## 安装

> ⚠️ **先读这段**：Steam 会从服务器重新拉取成就 schema，本地 BIN 的改动可能被还原，越新的客户端
> 越明显。因此推荐**方法 B**。

两种方法都需要**先完全退出 Steam**。

### 方法 A：直接替换（简单，但可能被还原）

1. 备份原文件（本仓库 `original/` 下就是原始文件）。
2. 把 `UserGameStatsSchema_1568400.bin` 覆盖到：

   ```
   <Steam 安装目录>\appcache\stats\UserGameStatsSchema_1568400.bin
   ```

3. 右键该文件 → 属性 → 勾选**只读** → 确定。
4. 重启 Steam。

Steam 若刷新了该游戏的 schema，改动会丢失，重新覆盖即可。

### 方法 B：SATLI（推荐，可抵抗 schema 刷新）

1. 安装 [SATLI](https://github.com/GaBoron/SATLI)（优先 Microsoft Store 版，或 GitHub Releases）。
2. 打开 SATLI，等它扫描完本机 Steam 游戏。
3. 用「本地导入」导入本仓库的 `UserGameStatsSchema_1568400.zip`（或 BIN 文件）。
4. 预览确认目标语言为**简体中文**，点安装 —— 关闭 Steam，同意 UAC。
5. 安装后启用 **「锁定 Steam 成就显示」**。这一步由 Millennium 插件在运行时覆盖 Steam 在线
   schema 与成就弹窗的显示，是当前能抵抗服务器刷新还原的办法。

SATLI 安装前会自动备份原文件，可在「已管理」页随时恢复。

---

## 汉化内容

完整英中对照见 [`汉化对照表.md`](汉化对照表.md)。名称一览：

| API ID | English | 简体中文 | API ID | English | 简体中文 |
| --- | --- | --- | --- | --- | --- |
| `vinyl0` | Vinyl #0 | 黑胶唱片 #0 | `speedrun2` | Hello, speedrunner. | 你好，速通玩家。 |
| `vinyl1` | Vinyl #1 | 黑胶唱片 #1 | `flower` | It's just a flower... | 只是一朵花…… |
| `vinyl2` | Vinyl #2 | 黑胶唱片 #2 | `door` | Open the door! | 开门！ |
| `vinyl3` | Vinyl #3 | 黑胶唱片 #3 | `records` | Lore master | 考据大师 |
| `vinyl4` | Vinyl #4 | 黑胶唱片 #4 | `trap` | Ancient trap | 古老的陷阱 |
| `vinyl5` | Vinyl #5 | 黑胶唱片 #5 | `run` | The way of the rabbit | 兔子之道 |
| `phone` | Hello? | 喂？ | `patches2` | Complicated relationship | 复杂的关系 |
| `fly` | I believe I can fly | 我相信我能飞 | `paris` | Oh! | 哦！ |
| `skill1` | Double jump! | 二段跳！ | `easteregg` | You found Sheepy! | 你找到了 Sheepy！ |
| `skill2` | Time to run! | 该跑了！ | `portal` | The End | 剧终 |
| `skill3` | Weird magic... | 奇怪的魔法…… | `nodeath` | SHEEPY STRONG | SHEEPY 最强 |
| `scary` | What? | 什么？ | `dontgiveup` | It's a hard one... | 这确实很难…… |
| `patches1` | Hi Patches! | 你好，PATCHES！ | `voice` | Your destiny... | 你的命运…… |
| `elevator` | It's working! | 能用了！ | `crystals` | Shine bright like a crystal | 像水晶一样闪耀 |
| `chair` | You spin me right 'round | 你让我转个不停 | `speedrun1` | That's a record! | 破纪录了！ |

### 术语与风格

翻译的首要依据是**游戏自己的官方简中**，不是英文直译。游戏是 NW.js 打包的，`package.nw` 里的
`languages.json`（语言索引 4 = 简体中文）是官方简中资源，据此锁定：

- **PATCHES**（兔子角色）在官方简中里保留拉丁大写，不译为「补丁」。
- **lever → 控制杆**（游戏内原文「重新拉下控制杆」）。
- **Ancient trap → 古老的陷阱**（对齐游戏内「古老的陷阱不适合我」）。
- **Archaeologist → 考古学家**、**crystal → 水晶**、**Engineer → 工程师**。
- **The End → 剧终**，取自官方片尾译法。

其他取向：

- 专有名词 Sheepy / PATCHES / Belgin 保留拉丁原文。
- 标点统一用规范全角。注意游戏自身简中的标点**不统一**——同一段里混用半角 `, . ? !` 与全角 `，！`。
  成就显示在 Steam 悬浮窗、走 Steam 自带中文字体，不受游戏字体限制，故按规范排版处理。
- 数字与西文两侧留空格（「45 分钟内」「6 个控制杆」）。
- 保留原文的梗与语气：`speedrun1` 的 record 双关（纪录／唱片，中文无法兼顾，取「纪录」义）、
  `skill2` 的索尼克梗 GOTTA GO FAST、`chair` 的歌曲《You Spin Me Round》、
  `crystals` 戏仿「Shine bright like a diamond」。逐条说明见对照表「译者注」。

---

## 校验

改动是**纯追加**：只往每条成就的 `display/name` 与 `display/desc` 里加了 `schinese` 节点，
其余一律未动。`tools/verify.py` 会独立重新解析输入与输出并逐项核对，实测全部通过：

| 检查 | 结果 |
| --- | --- |
| 输入／输出 BIN 解析后重新序列化是否**逐字节相同** | 是（8 601 B / 10 524 B） |
| 结构差异 | 仅新增 60 个节点，无删除、无其它字段改动 |
| 新增节点位置 | 全部为 `display/name/schinese` 与 `display/desc/schinese` |
| 节点顺序 | 除 name/desc 内追加外完全保持；60/60 为 `[english, token, schinese]` |
| `english` / `token` / `hidden` / `icon` / `icon_gray` | 逐条比对，未被改动 |
| 成就数量与顺序 | 仍为 30 条且顺序不变 |
| `gamename` / `version` / `stats.type` | 未改动 |
| 本地 schema 与线上成就列表 | 线上 30 条，API 名集合完全一致，无版本漂移 |
| 投稿 ZIP | 根目录仅含一个 BIN，内容与根目录 BIN 一致 |

自己复核：

```bash
python tools/verify.py --input original/UserGameStatsSchema_1568400.bin \
                       --final UserGameStatsSchema_1568400.bin \
                       --csv work/translations.csv
```

**未做的事**：没有在 Steam 里实际加载验证过——那需要关闭 Steam 并取得管理员权限去写 `appcache`，
属于会改动 Steam 安装目录的操作，留给使用者自行决定。文件格式已按已知可用的同类文件同构校验。

---

## 改译文 / 重新构建

```bash
# 1) 编辑 work/translations.csv 的 target_name / target_description
# 2) 重新构建（需要 GaBoron/steam-achievement-localizer-skill）
python <skill>/scripts/steam_bkv_tool.py apply --workspace <本工程目录>
# 3) 独立校验
python tools/verify.py --input original/UserGameStatsSchema_1568400.bin \
                       --final UserGameStatsSchema_1568400.bin \
                       --csv work/translations.csv
```

---

## 制作方式

做法参照 [Ifover/SteamAchievementsCHS](https://github.com/Ifover/SteamAchievementsCHS)：在 Valve
二进制 KeyValues（`UserGameStatsSchema_<appid>.bin`）里为每条成就追加 `display/name/schinese` 与
`display/desc/schinese` 节点，节点位置紧随 `token` 之后——与该项目既有文件的写法一致。

构建与校验走 [GaBoron/steam-achievement-localizer-skill](https://github.com/GaBoron/steam-achievement-localizer-skill)
的工具链，产出其标准投稿 ZIP，因此也能直接提交到
[Steam 成就翻译库](https://github.com/GaBoron/steam-achievement-translation-library)。

## 来源

- 写法参照：[Ifover/SteamAchievementsCHS](https://github.com/Ifover/SteamAchievementsCHS)（MIT）
- 工具链：[GaBoron/steam-achievement-localizer-skill](https://github.com/GaBoron/steam-achievement-localizer-skill)（MIT）
- 安装器：[GaBoron/SATLI](https://github.com/GaBoron/SATLI)（MIT）
- 官方商店页：<https://store.steampowered.com/app/1568400/>
- 成就解锁率：Steam Web API `GetGlobalAchievementPercentagesForApp`
- 术语首要依据：游戏本体 `package.nw` → `languages.json`（官方简中，语言索引 4）
- 翻译库查询：无本游戏条目，故 30 条均为新译，无既有译本可比对

## 已知限制

- 译文未经母语审校，也未经社区验证。术语已尽量对齐官方简中，但**梗与语气**的判断
  （如 `skill1` 的 Taking You Higher、`speedrun1` 的 record 双关）属译者取舍。
- `paris`、`flower` 两条的成就名指向游戏内具体情境，未找到第一方或社群的一手说明，按字面与语气翻译。

## 许可

本仓库的译文与脚本采用 MIT 许可，见 [LICENSE](LICENSE)。
Steam 成就 schema 的原始数据结构归 Valve 与游戏开发者所有。
