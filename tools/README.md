# tools

只用 Python 标准库，无第三方依赖。Python 3.8+。

## kvbin.py — Valve 二进制 KeyValues 编解码器

Steam 的 `UserGameStatsSchema_<appid>.bin` 是 Valve 二进制 KeyValues 格式。本模块把它解析成
保留**类型与顺序**的树，并能原样序列化回去。

```python
import kvbin

root, pos, raw = kvbin.load("UserGameStatsSchema_1568400.bin")   # 解析
assert kvbin.serialize(root) == raw                              # 逐字节回环校验
```

节点是 `(type_byte, name, value)` 三元组，对象是这些三元组的列表：

| type | 含义 | value 类型 |
| --- | --- | --- |
| `0x00` | 嵌套对象 | `Obj`（即列表） |
| `0x01` | 字符串（UTF-8，以 NUL 结尾） | `str` |
| `0x02` / `0x04` / `0x07` | int32 / uint32 / uint64 | `int` |
| `0x03` | float32 | `float` |

对象以单个 `0x08` 字节结束。

`Obj` 提供 `find(name)` / `get(name)` / `set(name, value)` / `keys()`。注意 `get()` **不接受默认值**，
取不到返回 `None`。

**关键点：改任何二进制格式之前，先证明解析后再序列化能逐字节还原原文件。** 只有回环成立，追加
节点才是安全的；否则你写的每一个字节都在赌。`verify.py` 的第 1 项就是干这个的。

## verify.py — 独立校验

重新解析原始 schema 与汉化后的 schema，比对两棵树，断言差异**只有**新增的
`display/name/schinese` 与 `display/desc/schinese`，其余节点、取值、顺序、token、图标、隐藏标记
一律未变。

```bash
python tools/verify.py
python tools/verify.py --input original/UserGameStatsSchema_1568400.bin \
                       --final UserGameStatsSchema_1568400.bin \
                       --csv work/translations.csv
```

不带参数时按 `localization/<appid>-<language>/` 工程布局找文件；`--csv` 不存在时会跳过文本比对，
其余检查照跑。全部通过时退出码为 0。

检查项：回环逐字节一致、源文件哈希未变、无删除无改动、恰好新增 60 个节点、新增位置合法、
节点顺序仅在 name/desc 尾部追加、`[english, token, schinese]` 排列合规、译文与 CSV 一致、
`english`/`token`/`hidden`/`icon`/`icon_gray` 未动、成就数量与顺序不变、`gamename`/`version`/
`stats.type` 未动。
