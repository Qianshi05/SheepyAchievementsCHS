# Steam 成就汉化

给本体自带官方简中、但 Steam 成就只有英文的游戏补上中文成就。

## 文件对照

根目录里的 `.bin` 就是成品，一行一个游戏。**文件名不能改**——Steam 按
`UserGameStatsSchema_<appid>.bin` 这个名字读取，改成游戏名会失效。

下表顺序与仓库根目录的文件列表顺序一致。

| 文件 | 游戏 | AppID | 成就数 |
| --- | --- | --- | --- |
| `UserGameStatsSchema_105600.bin` | Terraria / 泰拉瑞亚 | 105600 | 137 |
| `UserGameStatsSchema_1222140.bin` | Detroit: Become Human / 底特律：化身为人 | 1222140 | 48 |
| `UserGameStatsSchema_1326470.bin` | Sons Of The Forest / 森林之子 | 1326470 | 32 |
| `UserGameStatsSchema_1568400.bin` | Sheepy: A Short Adventure | 1568400 | 30 |
| `UserGameStatsSchema_242760.bin` | The Forest / 森林 | 242760 | 45 |
| `UserGameStatsSchema_346110.bin` | ARK: Survival Evolved / 方舟：生存进化 | 346110 | 32 |
| `UserGameStatsSchema_403640.bin` | Dishonored 2 / 耻辱2 | 403640 | 50 |
| `UserGameStatsSchema_508440.bin` | Totally Accurate Battle Simulator / 全面战争模拟器 | 508440 | 64 |
| `UserGameStatsSchema_632360.bin` | Risk of Rain 2 / 雨中冒险 2 | 632360 | 171 |
| `UserGameStatsSchema_815370.bin` | Green Hell / 绿色地狱 | 815370 | 68 |

共 10 款游戏、677 条成就。非官方民间汉化，游戏内容版权归各开发者。

## 安装

先完全退出 Steam。

**推荐** —— 用 [SATLI](https://github.com/GaBoron/SATLI) 导入投稿 ZIP（在 `资料归档.zip` 里，
文件名同样是 `UserGameStatsSchema_<appid>.zip`），装完开启「锁定 Steam 成就显示」。
Steam 会从服务器刷新成就 schema，直接替换本机文件可能被还原。

**手动** —— 把上表对应的 `.bin` 覆盖到 `<Steam>\appcache\stats\`，设为只读，重启 Steam。

## 资料归档.zip

除根目录的 10 个 `.bin` 之外，其余材料全部收在这个包里（77 个成员）：

```
UserGameStatsSchema_<appid>.zip    标准投稿 ZIP，供 SATLI 导入
games/<appid>/                     该游戏的译文、来源记录、校验报告、对照表
games/<appid>/original/            未改动的原始 schema，用于还原
tools/                             二进制 KeyValues 编解码 + 独立校验脚本
```

`games/<appid>/` 目录名用的是 AppID，对应关系见上表；每个目录里也有 `manifest.json` 记录
`app_id` 与源文件哈希。

## 说明

- 只在每条成就的 `display/name` 与 `display/desc` 下追加 `schinese`，其余字段一律不动；
  改动可用归档里的 `tools/verify.py` 逐字节校验。
- 译文未经母语审校，欢迎 issue / PR。

## 制作

写法借鉴 [Ifover/SteamAchievementsCHS](https://github.com/Ifover/SteamAchievementsCHS)，
工具链用 [GaBoron/steam-achievement-localizer-skill](https://github.com/GaBoron/steam-achievement-localizer-skill)。

## 许可

译文与脚本 [MIT](LICENSE)；Steam 成就 schema 的结构与原始文本归 Valve 与各游戏开发者所有。
