"""Independent verification of a localized Steam achievement schema.

Re-parses input and output with an independent codec, walks both trees and
asserts that the ONLY difference is the addition of one language to every
achievement's display/name and display/desc, with every other node, value,
ordering, token, icon and hidden flag left untouched.

Usage:
    python verify.py --input <pristine.bin> --final <localized.bin> \
                     --csv <translations.csv> [--target-language schinese]

Defaults match the localization/<appid>-<language>/ project layout. --csv is
optional (text comparison is skipped if the file is absent).
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


def achievement_bits(root, app_id):
    out = []
    for grp in root.get(app_id).get("stats"):
        g = grp[2]
        if g.get("type") != "ACHIEVEMENTS":
            continue
        bits = g.get("bits")
        if bits is not None:
            out.extend(bits)
    return out


def main():
    parser = argparse.ArgumentParser(description="verify a localized achievement schema")
    parser.add_argument("--input", default=ORIG, help="pristine source schema")
    parser.add_argument("--final", default=FINAL, help="localized schema to verify")
    parser.add_argument("--csv", default=CSV_PATH, help="reviewed translations")
    parser.add_argument("--app-id", default=APP_ID)
    parser.add_argument("--target-language", default="schinese")
    parser.add_argument("--expect-source-sha", default=None,
                        help="fail unless the source file has this sha256")
    args = parser.parse_args()
    lang = args.target_language
    app_id = args.app_id

    print("=== 1. independent codec: byte-exact round-trip ===")
    for label, path in (("input", args.input), ("final", args.final)):
        root, pos, data = kvbin.load(path)
        out = kvbin.serialize(root)
        check("%s round-trip byte-identical (%d B)" % (label, len(data)),
              out == data and pos == len(data))
        if label == "input":
            orig_root = root
        else:
            fin_root = root

    print()
    print("=== 2. source file integrity ===")
    src_sha = hashlib.sha256(open(args.input, "rb").read()).hexdigest()
    if args.expect_source_sha:
        check("source sha256 matches expected", src_sha == args.expect_source_sha, src_sha)
    else:
        print("  [SKIP] no --expect-source-sha given; source sha256 = %s" % src_sha)

    print()
    print("=== 3. structural diff (input -> final) ===")
    orig_bits = achievement_bits(orig_root, app_id)
    fin_bits = achievement_bits(fin_root, app_id)
    n_ach = len(orig_bits)
    lo, lf, oo, of = {}, {}, {}, {}
    walk(orig_root, "", lo, oo)
    walk(fin_root, "", lf, of)
    added = sorted(set(lf) - set(lo))
    removed = sorted(set(lo) - set(lf))
    changed = [k for k in (set(lo) & set(lf)) if lo[k] != lf[k]]
    check("nothing removed", not removed, "; ".join(removed[:5]))
    check("nothing changed outside additions", not changed, "; ".join(changed[:5]))
    check("achievement count unchanged (%d)" % n_ach, len(fin_bits) == n_ach)
    check("exactly %d nodes added (2 per achievement)" % (2 * n_ach),
          len(added) == 2 * n_ach, "got %d" % len(added))

    want_name = "/display/name/" + lang
    want_desc = "/display/desc/" + lang
    bad_added = [p for p in added if not (p.endswith(want_name) or p.endswith(want_desc))]
    check("every added node is display/{name,desc}/%s" % lang, not bad_added,
          "; ".join(bad_added[:5]))
    n_names = sum(1 for p in added if p.endswith(want_name))
    n_descs = sum(1 for p in added if p.endswith(want_desc))
    check("%d name + %d desc nodes" % (n_ach, n_ach), n_names == n_ach and n_descs == n_ach,
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
                       and after[-1][1] == lang
                       and k.endswith(("/display/name", "/display/desc")))
            if not tail_ok:
                order_diffs.append(k)
    check("all key-order changes are a %s appended at the tail" % lang, not order_diffs,
          "; ".join(order_diffs[:5]))

    print()
    print("=== 5. target language appended last in every name/desc object ===")
    conform = total = non_object = 0
    for path in lf:
        # only achievement entries: some games also carry plain stat groups under
        # stats/<n>/ whose display/name is a bare string, not an object.
        if "/bits/" not in path:
            continue
        if path.endswith("/display/name") or path.endswith("/display/desc"):
            total += 1
            obj = fin_root
            for part in [p for p in path.split("/") if p]:
                obj = obj.get(part)
            if not hasattr(obj, "keys"):
                non_object += 1
                continue
            if obj.keys()[-1] == lang:
                conform += 1
    check("all %d name/desc objects end with %s" % (total, lang),
          total > 0 and conform == total and not non_object,
          "%d/%d conform, %d not objects" % (conform, total, non_object))

    print()
    print("=== 6. localized text matches the reviewed CSV ===")
    if os.path.exists(args.csv):
        with open(args.csv, "r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        by_id = {r["api_name"]: r for r in rows}
        check("CSV row count matches achievements", len(rows) == len(fin_bits),
              "csv=%d schema=%d" % (len(rows), len(fin_bits)))
        mismatches = []
        for entry in fin_bits:
            api = entry[2].get("name")
            disp = entry[2].get("display")
            row = by_id.get(api)
            if row is None:
                mismatches.append("%s: id not in CSV" % api)
                continue
            if disp.get("name").get(lang) != row["target_name"]:
                mismatches.append("%s name" % api)
            if disp.get("desc").get(lang) != row["target_description"]:
                mismatches.append("%s desc" % api)
        check("all achievements match CSV name+desc", not mismatches,
              "; ".join(mismatches[:5]))
    else:
        print("  [SKIP] translations CSV not found at %s" % args.csv)

    print()
    print("=== 7. every non-target field untouched (checked for all) ===")
    problems = []
    for eo, ef in zip(orig_bits, fin_bits):
        if eo[2].get("name") != ef[2].get("name"):
            problems.append("id order")
        do, df = eo[2].get("display"), ef[2].get("display")
        for field in ("name", "desc"):
            so, sf = do.get(field), df.get(field)
            if so is None or sf is None:
                continue
            for k in so.keys():
                if k == lang:
                    continue
                if so.get(k) != sf.get(k):
                    problems.append("%s %s.%s" % (eo[2].get("name"), field, k))
        for field in ("hidden", "icon", "icon_gray"):
            if do.get(field) != df.get(field):
                problems.append("%s %s" % (eo[2].get("name"), field))
    check("no non-target field altered, order identical", not problems,
          "; ".join(problems[:5]))

    print()
    print("=== 8. app-level fields untouched ===")
    for field in ("version", "gamename"):
        check("%s.%s unchanged" % (app_id, field),
              orig_root.get(app_id).get(field) == fin_root.get(app_id).get(field))
    check("stats group types unchanged",
          [g[2].get("type") for g in orig_root.get(app_id).get("stats")]
          == [g[2].get("type") for g in fin_root.get(app_id).get("stats")])

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
