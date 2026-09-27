"""Independent verification of a localized Steam achievement schema.

Re-parses input and output with an independent codec, walks both trees and
asserts that the ONLY difference is the addition of
display/name/schinese and display/desc/schinese nodes, with every other node,
value, ordering, token, icon and hidden flag left untouched.

Usage (defaults match the localization/<appid>-<language>/ project layout):
    python verify.py
    python verify.py --input original.bin --final localized.bin --csv translations.csv
"""
import argparse
import csv
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import kvbin  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.join(ROOT, "localization", "1568400-schinese")

APP_ID = "1568400"
SOURCE_SHA256 = "75f1d1f6a337c539e212133dbd6ebf4b10ef318ef4b605ed98828c415ab8a911"

ORIG = os.path.join(WS, "input", "UserGameStatsSchema_%s.bin" % APP_ID)
FINAL = os.path.join(WS, "final", "UserGameStatsSchema_%s.bin" % APP_ID)
CSV_PATH = os.path.join(WS, "work", "translations.csv")

failures = []


def check(label, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", label, ("  -- " + detail) if detail else ""))
    if not ok:
        failures.append(label)


def walk(obj, prefix, leaves, order):
    seen = {}
    names = []
    for t, name, value in obj:
        seen[name] = seen.get(name, 0) + 1
        key = name if seen[name] == 1 else "%s#%d" % (name, seen[name])
        names.append((t, name))
        path = prefix + "/" + key
        if t == kvbin.OBJ:
            leaves[path] = ("OBJ", None)
            walk(value, path, leaves, order)
        else:
            leaves[path] = (t, value)
    order[prefix] = names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=ORIG, help="pristine source schema")
    parser.add_argument("--final", default=FINAL, help="localized schema to verify")
    parser.add_argument("--csv", default=CSV_PATH, help="reviewed translations")
    args = parser.parse_args()

    print("=== 1. independent codec: byte-exact round-trip ===")
    for label, path in (("input", args.input), ("final", args.final)):
        root, pos, data = kvbin.load(path)
        out = kvbin.serialize(root)
        check("%s round-trip byte-identical (%d B)" % (label, len(data)),
              out == data and pos == len(data))
        if label == "input":
            orig_root, orig_data = root, data
        else:
            fin_root, fin_data = root, data

    print()
    print("=== 2. sha256 of input must be unchanged ===")
    with open(args.input, "rb") as fh:
        src_sha = hashlib.sha256(fh.read()).hexdigest()
    check("input sha256 matches expected source",
          src_sha == SOURCE_SHA256, src_sha)
    check("input file still %d bytes" % 8601, len(orig_data) == 8601, str(len(orig_data)))

    print()
    print("=== 3. structural diff (input -> final) ===")
    lo, lf, oo, of = {}, {}, {}, {}
    walk(orig_root, "", lo, oo)
    walk(fin_root, "", lf, of)
    added = sorted(set(lf) - set(lo))
    removed = sorted(set(lo) - set(lf))
    changed = [k for k in (set(lo) & set(lf)) if lo[k] != lf[k]]
    check("nothing removed", not removed, "; ".join(removed[:5]))
    check("nothing changed outside additions", not changed, "; ".join(changed[:5]))
    check("exactly 60 nodes added", len(added) == 60, "got %d" % len(added))

    bad_added = [p for p in added
                 if not p.endswith("/display/name/schinese")
                 and not p.endswith("/display/desc/schinese")]
    check("every added node is display/{name,desc}/schinese", not bad_added,
          "; ".join(bad_added[:5]))

    n_names = sum(1 for p in added if p.endswith("/display/name/schinese"))
    n_descs = sum(1 for p in added if p.endswith("/display/desc/schinese"))
    check("30 name + 30 desc nodes", n_names == 30 and n_descs == 30,
          "names=%d descs=%d" % (n_names, n_descs))

    print()
    print("=== 4. ordering preserved everywhere except inside name/desc ===")
    order_diffs = []
    for k in set(oo) | set(of):
        if oo.get(k) != of.get(k):
            before = oo.get(k) or []
            after = of.get(k) or []
            tail_ok = (len(after) == len(before) + 1
                       and after[:len(before)] == before
                       and after[-1][1] == "schinese"
                       and k.endswith(("/display/name", "/display/desc")))
            if not tail_ok:
                order_diffs.append(k)
    check("all key-order changes are a schinese appended at the tail", not order_diffs,
          "; ".join(order_diffs[:5]))

    print()
    print("=== 5. schinese placement matches the reference repo convention ===")
    conform = 0
    total = 0
    for path in lf:
        if path.endswith("/display/name") or path.endswith("/display/desc"):
            total += 1
            obj = fin_root
            for part in [p for p in path.split("/") if p]:
                obj = obj.get(part)
            keys = obj.keys()
            if keys[:2] == ["english", "token"] and keys[-1] == "schinese":
                conform += 1
    check("all %d name/desc objects are [english, token, schinese]" % total,
          conform == total, "%d/%d conform" % (conform, total))

    print()
    print("=== 6. localized text matches the reviewed CSV ===")
    if os.path.exists(args.csv):
        with open(args.csv, "r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        by_id = {r["api_name"]: r for r in rows}
        sroot = fin_root.get(APP_ID).get("stats").get("1").get("bits")
        check("achievement count still 30", len(sroot) == 30, str(len(sroot)))
        mismatches = []
        for entry in sroot:
            api = entry[2].get("name")
            disp = entry[2].get("display")
            row = by_id.get(api)
            if row is None:
                mismatches.append("%s: id not in CSV" % api)
                continue
            if disp.get("name").get("schinese") != row["target_name"]:
                mismatches.append("%s name" % api)
            if disp.get("desc").get("schinese") != row["target_description"]:
                mismatches.append("%s desc" % api)
        check("all 30 achievements match CSV name+desc", not mismatches,
              "; ".join(mismatches[:5]))
    else:
        print("  [SKIP] translations CSV not found at %s" % args.csv)

    print()
    print("=== 7. english/token/hidden/icon untouched (checked for all) ===")
    orig_bits = orig_root.get(APP_ID).get("stats").get("1").get("bits")
    sroot = fin_root.get(APP_ID).get("stats").get("1").get("bits")
    problems = []
    for eo, ef in zip(orig_bits, sroot):
        if eo[2].get("name") != ef[2].get("name"):
            problems.append("id order")
        do, df = eo[2].get("display"), ef[2].get("display")
        for field in ("english", "token"):
            if do.get("name").get(field) != df.get("name").get(field):
                problems.append("%s name.%s" % (eo[2].get("name"), field))
            if do.get("desc").get(field) != df.get("desc").get(field):
                problems.append("%s desc.%s" % (eo[2].get("name"), field))
        for field in ("hidden", "icon", "icon_gray"):
            if do.get(field) != df.get(field):
                problems.append("%s %s" % (eo[2].get("name"), field))
    check("no non-schinese field altered, order identical", not problems,
          "; ".join(problems[:5]))

    print()
    print("=== 8. gamename/version/type untouched ===")
    for field in ("version", "gamename"):
        check("%s.%s unchanged" % (APP_ID, field),
              orig_root.get(APP_ID).get(field) == fin_root.get(APP_ID).get(field))
    check("stats group type still ACHIEVEMENTS",
          fin_root.get(APP_ID).get("stats").get("1").get("type") == "ACHIEVEMENTS")

    print()
    if failures:
        print("RESULT: %d CHECK(S) FAILED" % len(failures))
        for f in failures:
            print("   -", f)
        return 1
    print("RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
