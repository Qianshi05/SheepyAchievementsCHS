# Steam 成就汉化

给本体自带官方简中、但 Steam 成就只有英文的游戏补上中文成就。

| AppID | 游戏 | 成就数 | 文件 |
| --- | --- | --- | --- |
| 1568400 | Sheepy: A Short Adventure | 30 | `UserGameStatsSchema_1568400.bin` |

非官方民间汉化，游戏内容版权归各开发者。

## 安装

先完全退出 Steam。

**推荐** —— 用 [SATLI](https://github.com/GaBoron/SATLI) 导入对应的 `.zip`，装完开启「锁定 Steam 成就显示」。
Steam 会从服务器刷新成就 schema，直接替换本机文件可能被还原。

**手动** —— 把 `.bin` 覆盖到 `<Steam>\appcache\stats\`，设为只读，重启 Steam。
原始文件在 `original/` 下，可随时还原。

## 仓库内容

```
UserGameStatsSchema_<appid>.bin    汉化后的 schema
UserGameStatsSchema_<appid>.zip    标准投稿 ZIP，供 SATLI 导入
original/                          未改动的原始 schema，用于还原
work/                              译文、来源记录与校验报告
汉化对照表.md                       英中对照 + 逐条译者注
tools/                             二进制 KeyValues 编解码 + 独立校验脚本
```

## 说明

- 只在每条成就的 `display/name` 与 `display/desc` 下追加 `schinese`，其余字段一律不动。
- 译文未经母语审校，欢迎 issue / PR。

## 制作

写法借鉴 [Ifover/SteamAchievementsCHS](https://github.com/Ifover/SteamAchievementsCHS)，
工具链用 [GaBoron/steam-achievement-localizer-skill](https://github.com/GaBoron/steam-achievement-localizer-skill)。

## 许可

译文与脚本 [MIT](LICENSE)；Steam 成就 schema 的结构与原始文本归 Valve 与各游戏开发者所有。
