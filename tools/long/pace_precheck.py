#!/usr/bin/env python3
"""Precheck sentence pacing estimates from script lines."""
import argparse
import re


def syl(s):
    s = s.replace("**", "")
    n = 0
    for w in re.findall(r"[\wÀ-ỹ]+", s):
        n += (2 if len(w) == 4 else 1) if w.isdigit() else 1
    return n


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    for f in args.files:
        t = 0.0
        for i, l in enumerate(open(f, encoding="utf-8").read().split("\n"), 1):
            if not l.strip(): continue
            d = 0.37 * syl(l) + 0.25  # hệ số hiệu chỉnh theo thời lượng render đo được
            if t < 12 * 60 and syl(l) >= 10 and not (l.startswith("**") and l.endswith("**")):
                print(f"{f}:{i} {syl(l)}t {d:.1f}s | {l}")
            t += d


if __name__ == "__main__":
    main()
