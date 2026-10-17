#!/usr/bin/env python3
"""
gpower-clone CLI — ANOVA: Fixed effects, omnibus, one-way (K3)
==============================================================
CLI contract as defined in the assignment (CONTRACT.md).

Usage:
  gpower-clone --test anova-oneway --mode a-priori  --f 0.25 --alpha 0.05 --power 0.80 --k 3
  gpower-clone --test anova-oneway --mode post-hoc  --f 0.25 --alpha 0.05 --n-total 159 --k 3

Output: single-line JSON to stdout.
  Success: {"n_total":<int>,"n_per_group":<int>,"actual_power":<float>,"critical_f":<float>,"df1":<int>,"df2":<int>,"ncp":<float>}
  Error  : {"error":"<description>"}  (exit code 1)
"""

from __future__ import annotations

import argparse
import json
import sys

from engine import a_priori, post_hoc, _validate_inputs


def _round4(v: float) -> float:
    """Round to 4 decimal places for output (G*Power shows 4 decimals)."""
    return round(v, 4)


def _round7(v: float) -> float:
    """Round to 7 decimal places for ncp / actual_power."""
    return round(v, 7)


def _error(msg: str) -> None:
    print(json.dumps({"error": msg}))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="gpower-clone: ANOVA one-way power analysis"
    )
    parser.add_argument("--test", required=True, help="Test identifier (anova-oneway)")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["a-priori", "post-hoc"],
        help="Analysis mode",
    )
    parser.add_argument("--f", type=float, dest="effect_f", help="Cohen's f effect size")
    parser.add_argument("--alpha", type=float, help="Type I error rate")
    parser.add_argument("--power", type=float, help="Target power (a-priori only)")
    parser.add_argument("--k", type=int, help="Number of groups")
    parser.add_argument("--n-total", type=int, dest="n_total", help="Total sample size (post-hoc only)")

    args = parser.parse_args()

    # Validate test identifier
    if args.test != "anova-oneway":
        _error(f"Unsupported test: '{args.test}'. This CLI supports: anova-oneway")

    # Common required parameters
    if args.effect_f is None:
        _error("--f (effect size) is required")
    if args.alpha is None:
        _error("--alpha is required")
    if args.k is None:
        _error("--k (number of groups) is required")

    try:
        if args.mode == "a-priori":
            if args.power is None:
                _error("--power is required for a-priori mode")

            result = a_priori(
                f=args.effect_f,
                alpha=args.alpha,
                power=args.power,
                k=args.k,
            )
            out = {
                "n_total": result.n_total,
                "n_per_group": result.n_per_group,
                "actual_power": _round7(result.actual_power),
                "critical_f": _round4(result.critical_f),
                "df1": result.df1,
                "df2": result.df2,
                "ncp": _round4(result.ncp),
            }

        else:  # post-hoc
            if args.n_total is None:
                _error("--n-total is required for post-hoc mode")

            result = post_hoc(
                f=args.effect_f,
                alpha=args.alpha,
                n_total=args.n_total,
                k=args.k,
            )
            out = {
                "actual_power": _round7(result.actual_power),
                "critical_f": _round4(result.critical_f),
                "df1": result.df1,
                "df2": result.df2,
                "ncp": _round4(result.ncp),
            }

        print(json.dumps(out))

    except ValueError as exc:
        _error(str(exc))
    except Exception as exc:
        _error(f"Internal error: {exc}")


if __name__ == "__main__":
    main()
