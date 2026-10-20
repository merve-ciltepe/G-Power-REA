"""
ANOVA One-Way Fixed Effects Power Analysis Engine
=================================================
Pure Clean-Room Implementation based strictly on SPEC.md.

Test Family : F tests
Statistical  : ANOVA: Fixed effects, omnibus, one-way
Modes        : a-priori  (compute sample size N given alpha, power, f, k)
               post-hoc  (compute power given alpha, N, f, k)

References:
  Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007).
    G*Power 3: A flexible statistical power analysis program for the
    social, behavioral, and biomedical sciences. Behavior Research Methods,
    39(2), 175-191.
  Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from scipy.stats import f as fdist, ncf

_MAX_N_SEARCH = 10_000_000


@dataclass
class APrioriResult:
    """Result of an a-priori (compute N) analysis."""
    n_total: int
    n_per_group: int          # exact equal group size (N = k * n_per_group)
    actual_power: float
    critical_f: float
    df1: int
    df2: int
    ncp: float                # noncentrality parameter lambda


@dataclass
class PostHocResult:
    """Result of a post-hoc (compute power) analysis."""
    actual_power: float
    critical_f: float
    df1: int
    df2: int
    ncp: float


def _ncp(f: float, n_total: int) -> float:
    """Noncentrality parameter lambda = f^2 * N."""
    return f * f * n_total


def _critical_f(alpha: float, df1: int, df2: int) -> float:
    """Upper-tail critical value: F such that P(F_{df1,df2} > F) = alpha."""
    return float(fdist.ppf(1.0 - alpha, df1, df2))


def _achieved_power(f_crit: float, df1: int, df2: int, lam: float) -> float:
    """Upper-tail probability: P(ncF_{df1,df2,lambda} > F_crit)."""
    return float(ncf.sf(f_crit, df1, df2, lam))


def a_priori(
    f: float,
    alpha: float,
    power: float,
    k: int | float,
) -> APrioriResult:
    """
    Compute the minimum total sample size N for one-way ANOVA.
    Strictly follows SPEC.md requirements:
      - Enforces balanced design (n1 = n2 = ... = nk).
      - Total sample size N is always a multiple of k.
    """
    f, alpha, power, k_norm, _ = _validate_and_normalize(f=f, alpha=alpha, power=power, k=k)
    assert k_norm is not None

    df1 = k_norm - 1

    # Balanced group design: iterate over n_per_group so N = k * n_per_group
    # Minimum n_per_group = 2 so df2 = N - k >= k >= 2.
    n_per_group = 2
    while n_per_group * k_norm <= _MAX_N_SEARCH:
        n = n_per_group * k_norm
        df2 = n - k_norm
        lam = _ncp(f, n)
        f_crit = _critical_f(alpha, df1, df2)
        pwr = _achieved_power(f_crit, df1, df2, lam)
        if pwr >= power:
            return APrioriResult(
                n_total=n,
                n_per_group=n_per_group,
                actual_power=pwr,
                critical_f=f_crit,
                df1=df1,
                df2=df2,
                ncp=lam,
            )
        n_per_group += 1

    raise RuntimeError(
        f"Could not reach target power {power} within N={_MAX_N_SEARCH}."
    )


def post_hoc(
    f: float,
    alpha: float,
    n_total: int | float,
    k: int | float,
) -> PostHocResult:
    """Compute achieved power for a given total sample size."""
    f, alpha, _, k_norm, n_norm = _validate_and_normalize(f=f, alpha=alpha, n_total=n_total, k=k)
    assert k_norm is not None and n_norm is not None

    df1 = k_norm - 1
    df2 = n_norm - k_norm
    lam = _ncp(f, n_norm)
    f_crit = _critical_f(alpha, df1, df2)
    pwr = _achieved_power(f_crit, df1, df2, lam)

    return PostHocResult(
        actual_power=pwr,
        critical_f=f_crit,
        df1=df1,
        df2=df2,
        ncp=lam,
    )


def _validate_and_normalize(
    f: float | None = None,
    alpha: float | None = None,
    power: float | None = None,
    k: int | float | None = None,
    n_total: int | float | None = None,
) -> tuple[float | None, float | None, float | None, int | None, int | None]:
    """Validate and normalize inputs according to SPEC.md."""
    errors: list[str] = []

    if f is not None:
        try:
            f = float(f)
            if not math.isfinite(f) or f <= 0:
                errors.append(f"Effect size f must be > 0, got {f}")
        except (ValueError, TypeError):
            errors.append(f"Invalid effect size f: {f}")

    if alpha is not None:
        try:
            alpha = float(alpha)
            if not math.isfinite(alpha) or not (0 < alpha < 1):
                errors.append(f"Alpha must be in (0, 1), got {alpha}")
        except (ValueError, TypeError):
            errors.append(f"Invalid alpha: {alpha}")

    if power is not None:
        try:
            power = float(power)
            if not math.isfinite(power) or not (0 < power < 1):
                errors.append(f"Power must be in (0, 1), got {power}")
            if alpha is not None and power <= alpha:
                errors.append(f"Power ({power}) must be greater than alpha ({alpha})")
        except (ValueError, TypeError):
            errors.append(f"Invalid power: {power}")

    k_int: int | None = None
    if k is not None:
        try:
            k_val = float(k)
            if not k_val.is_integer() or int(k_val) < 2:
                errors.append(f"Number of groups k must be integer >= 2, got {k}")
            else:
                k_int = int(k_val)
        except (ValueError, TypeError):
            errors.append(f"Invalid number of groups k: {k}")

    n_int: int | None = None
    if n_total is not None:
        try:
            n_val = float(n_total)
            if not n_val.is_integer() or int(n_val) < 1:
                errors.append(f"Total sample size must be integer >= 1, got {n_total}")
            else:
                n_int = int(n_val)
                if k_int is not None and n_int <= k_int:
                    errors.append(f"Total sample size ({n_int}) must be > k ({k_int}) so df2 >= 1")
        except (ValueError, TypeError):
            errors.append(f"Invalid total sample size: {n_total}")

    if errors:
        raise ValueError("; ".join(errors))

    return f, alpha, power, k_int, n_int
