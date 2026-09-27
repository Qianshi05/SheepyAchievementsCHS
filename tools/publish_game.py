"""Publish one localized game from the localizer workspace into the repo layout.

Root keeps the ready-to-use .bin/.zip; everything else goes to games/<appid>/.
Absolute local paths inside report.json / manifest.json are rewritten to
repo-relative ones so nothing about the author's machine leaks.

Usage:
    python tools/publish_game.py --app-id 815370 --title "Green Hell / 绿色地狱" \
        --workspace <localization workspace> --pristine <original .bin> \
        [--unlock-json <global percentages json>]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

BS = chr(92)


def sanitize(payload: dict, app_id: str) -> dict:
    """Rewrite any absolute author-machine path to a repo-relative one."""
    game = "games/%s" % app_id
    mapping = {}
    for key, value in payload.items():
        if isinstance(value, str) and (":" + BS) in value:
            name = os.path.basename(value.replace("/", BS))
            if name.startswith("UserGameStatsSchema_") and name.endswith(".bin"):
                # the pristine copy vs the localized one: both end up under the repo
                if "original" in value or "文件参考" in value or ("input" + BS) in value:
                    mapping[key] = "%s/original/%s" % (game, name)
                else:
                    mapping[key] = name
            elif name.endswith(".zip"):
                mapping[key] = name
            elif name.endswith(".json"):
                mapping[key] = "%s/%s" % (game, name)
    payload.update(mapping)
    return payload


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--app-id", required=True)
    p.add_argument("--workspace", required=True)
    p.add_argument("--pristine", required=True)
    p.add_argument("--repo", default=os.getcwd())
    p.add_argument("--title", default=None)
    p.add_argument("--unlock-json", default=None)
    args = p.parse_args()

    repo = args.repo
    ws = args.workspace
    app = args.app_id
    game_dir = os.path.join(repo, "games", app)
    os.makedirs(os.path.join(game_dir, "original"), exist_ok=True)

    bin_name = "UserGameStatsSchema_%s.bin" % app
    zip_name = "UserGameStatsSchema_%s.zip" % app
    copies = [
        (os.path.join(ws, "final", bin_name), os.path.join(repo, bin_name)),
        (os.path.join(ws, "final", zip_name), os.path.join(repo, zip_name)),
        (args.pristine, os.path.join(game_dir, "original", bin_name)),
        (os.path.join(ws, "work", "translations.csv"), os.path.join(game_dir, "translations.csv")),
        (os.path.join(ws, "work", "sources.json"), os.path.join(game_dir, "sources.json")),
    ]
    for src, dst in copies:
        if not os.path.exists(src):
            raise SystemExit("missing: %s" % src)
        shutil.copy2(src, dst)
        print("  copied ->", os.path.relpath(dst, repo).replace(BS, "/"))

    for name, src_dir in (("report.json", "final"), ("manifest.json", "work")):
        src = os.path.join(ws, src_dir, name)
        payload = json.load(open(src, encoding="utf-8"))
        payload = sanitize(payload, app)
        raw = json.dumps(payload, ensure_ascii=False, indent=2)
        leaked = [t for t in ("GAME相关", "E:" + BS, "localization" + BS + app) if t in raw]
        if leaked:
            raise SystemExit("%s still leaks local paths: %s" % (name, leaked))
        dst = os.path.join(game_dir, name)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(raw + "\n")
        print("  sanitized ->", "games/%s/%s" % (app, name))

    # review table
    cmd = [sys.executable, os.path.join(repo, "tools", "make_review_table.py"),
           "--app-id", app,
           "--final", os.path.join(repo, bin_name),
           "--csv", os.path.join(game_dir, "translations.csv"),
           "--out", os.path.join(game_dir, "对照表.md")]
    if args.title:
        cmd += ["--title", args.title]
    if args.unlock_json and os.path.exists(args.unlock_json):
        cmd += ["--unlock-json", args.unlock_json]
    subprocess.run(cmd, check=True)

    print()
    print("done: games/%s/" % app)


if __name__ == "__main__":
    main()
