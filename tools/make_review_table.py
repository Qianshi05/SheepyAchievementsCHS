"""Generate an EN/ZH review table for one game, straight from the shipped BIN.

The table is derived from the actual deliverable (not hand-transcribed) and
joined with Steam unlock rates when a GetGlobalAchievementPercentagesForApp
response is available.

Usage:
    python tools/make_review_table.py --app-id 815370 \
        --final UserGameStatsSchema_815370.bin \
        --csv   games/815370/translations.csv \
        --out   games/815370/对照表.md \
        [--unlock-json path/to/global_percentages.json] \
        [--title "Green Hell / 绿色地狱"] \
        [--target-language schinese]
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import kvbin  # noqa: E402


def gv(obj, key, default=""):
    """Obj.get with a default (kvbin.Obj.get takes no default)."""
    value = obj.get(key)
    return default if value is None else value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--app-id", required=True)
    p.add_argument("--final", required=True, help="localized schema")
    p.add_argument("--csv", required=True, help="reviewed translations")
    p.add_argument("--out", required=True, help="markdown output path")
    p.add_argument("--unlock-json", default=None)
    p.add_argument("--title", default=None)
    p.add_argument("--target-language", default="schinese")
    args = p.parse_args()
    lang = args.target_language

    root = kvbin.load(args.final)[0]
    bits = []
    for grp in root.get(args.app_id).get("stats"):
        g = grp[2]
        if g.get("type") != "ACHIEVEMENTS":
            continue
        b = g.get("bits")
        if b is not None:
            bits.extend(b)

    pct = {}
    if args.unlock_json and os.path.exists(args.unlock_json):
        live = json.load(open(args.unlock_json, encoding="utf-8"))
        pct = {a["name"]: float(a["percent"])
               for a in live["achievementpercentages"]["achievements"]}

    notes = {}
    if os.path.exists(args.csv):
        with open(args.csv, encoding="utf-8-sig", newline="") as fh:
            notes = {r["api_name"]: r.get("translation_notes", "")
                     for r in csv.DictReader(fh)}

    title = args.title or ("AppID %s 成就汉化对照表" % args.app_id)
    L = []
    L.append("# %s — 成就汉化对照表" % title)
    L.append("")
    L.append("> 本表由 `%s`（实际交付文件）直接解析生成，非手工转录。"
             % os.path.basename(args.final)
             + ("解锁率来自 Steam 官方接口。" if pct else ""))
    L.append("")
    L.append("| # | API ID | 隐藏 | 解锁率 | English | 简体中文 |")
    L.append("| --- | --- | :-: | --- | --- | --- |")
    for i, entry in enumerate(bits):
        api = entry[2].get("name")
        d = entry[2].get("display")
        hid = "是" if str(d.get("hidden")) == "1" else ""
        rate = ("%.2f%%" % pct[api]) if api in pct else "—"
        L.append("| %d | `%s` | %s | %s | **%s**<br/>%s | **%s**<br/>%s |" % (
            i, api, hid, rate,
            gv(d.get("name"), "english"), gv(d.get("desc"), "english"),
            gv(d.get("name"), lang), gv(d.get("desc"), lang)))

    L.append("")
    L.append("## 译者注（按成就）")
    L.append("")
    for entry in bits:
        api = entry[2].get("name")
        note = notes.get(api, "")
        if note:
            L.append("- **%s**（%s）：%s" % (gv(entry[2].get("display").get("name"), lang), api, note))
    L.append("")

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("wrote %s (%d achievements)" % (args.out, len(bits)))


if __name__ == "__main__":
    main()
