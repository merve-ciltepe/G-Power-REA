#!/usr/bin/env python3
"""
Differential test suite: gpower-clone vs G*Power 3.1.9.7 oracle.

Runs all oracle CSV vectors through the CLI and compares N values.
Reports match rate (must be >= 90% for gate to pass).

Usage:
    python tests/differential_test.py --oracle oracle/vectors.csv --cli src/cli.py
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def run_cli(cli_path: str, args: list[str]) -> dict:
    """Run gpower-clone CLI and return parsed JSON output."""
    cmd = [sys.executable, cli_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout.strip()), result.returncode
    except json.JSONDecodeError:
        return {"error": f"Could not parse output: {result.stdout!r}"}, 1


def compare_vectors(oracle_file: str, cli_path: str) -> None:
    vectors = list(csv.DictReader(open(oracle_file, newline="", encoding="utf-8")))
    total = len(vectors)
    n_match = 0
    mismatches = []

    print(f"Running {total} oracle vectors...\n")

    for i, row in enumerate(vectors):
        mode = row["mode"]
        cli_args = ["--test", "anova-oneway", "--mode", mode,
                    "--f", row["f"],
                    "--alpha", row["alpha"],
                    "--k", row["k"]]

        if mode == "a-priori":
            cli_args += ["--power", row["power"]]
            expected_n = int(row["n_total"])
        else:
            cli_args += ["--n-total", row["n_total"]]

        out, code = run_cli(cli_path, cli_args)

        if "error" in out:
            status = "ERROR"
            mismatches.append({
                "row": i + 1, "vector": dict(row),
                "status": status, "got": out
            })
            continue

        if mode == "a-priori":
            got_n = out.get("n_total")
            match = (got_n == expected_n)
            if match:
                n_match += 1
                status = "OK"
            else:
                status = "MISMATCH"
                mismatches.append({
                    "row": i + 1,
                    "vector": dict(row),
                    "expected_n": expected_n,
                    "got_n": got_n,
                    "got_power": out.get("actual_power"),
                    "status": status,
                })
        else:  # post-hoc: compare power to 4 decimal places
            expected_power = float(row["actual_power"])
            got_power = out.get("actual_power", 0.0)
            match = abs(got_power - expected_power) < 0.001
            if match:
                n_match += 1
                status = "OK"
            else:
                status = "MISMATCH"
                mismatches.append({
                    "row": i + 1,
                    "vector": dict(row),
                    "expected_power": expected_power,
                    "got_power": got_power,
                    "status": status,
                })

        print(f"  [{i+1:3d}] {status:10s} | mode={mode} f={row['f']} alpha={row['alpha']} k={row['k']}", end="")
        if mode == "a-priori":
            print(f" power={row['power']} -> expected_N={row['n_total']} got_N={out.get('n_total','?')}")
        else:
            print(f" N={row['n_total']} -> expected_pwr={row.get('actual_power','?')} got_pwr={out.get('actual_power','?')}")

    match_rate = n_match / total * 100
    print(f"\n{'='*60}")
    print(f"Match rate: {n_match}/{total} = {match_rate:.1f}%")
    print(f"Gate (>=90%): {'PASS [OK]' if match_rate >= 90 else 'FAIL [X]'}")

    if mismatches:
        print(f"\nMismatches ({len(mismatches)}):")
        for m in mismatches:
            print(f"  Row {m['row']}: {m}")

    sys.exit(0 if match_rate >= 90 else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", default="oracle/vectors.csv")
    parser.add_argument("--cli", default="src/cli.py")
    args = parser.parse_args()
    compare_vectors(args.oracle, args.cli)
