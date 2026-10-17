"""
ANOVA One-Way Fixed Effects Power Analysis Engine
=================================================
Test Family : F tests
Statistical  : ANOVA: Fixed effects, omnibus, one-way
Modes        : a-priori  (compute N given alpha, power, f, k)
               post-hoc  (compute power given alpha, N, f, k)

Algorithm reconstructed from G*Power 3.1.9.7 binary analysis (Session 1).
References:
  Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007).
    G*Power 3: A flexible statistical power analysis program for the
    social, behavioral, and biomedical sciences. Behavior Research Methods,
    39(2), 175-191.
  Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009).
    Statistical power analyses using G*Power 3.1: Tests for correlation
    and regression analyses. Behavior Research Methods, 41(4), 1149-1160.
  Cohen, J. (1988). Statistical power analysis for the behavioral sciences
    (2nd ed.). Lawrence Erlbaum Associates.

[DOK] Effect size f (Cohen's f):  f = sigma_m / sigma
      sigma_m = SD of group means; sigma = within-group SD
[DOK] Noncentrality parameter:     lambda = f^2 * N   (N = total sample size)
[DOK] Numerator df:                df1 = k - 1
[DOK] Denominator df:              df2 = N - k
[DOK] Critical F:                  F_crit = F_quantile(1 - alpha, df1, df2)
[DOK] Achieved power:              1 - CDF_ncF(F_crit; df1, df2, lambda)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from scipy.stats import f as fdist, ncf


# ---------------------------------------------------------------------------
# Constants derived from binary string scan of GPowerNT.exe
# [REA] 0x001c89b8: "f = .10 - small"
# [REA] 0x001c89c8: "f = .25 - medium"
# [REA] 0x001c89d9: "f = .40 - large"
# ---------------------------------------------------------------------------
EFFECT_SIZE_SMALL = 0.10
EFFECT_SIZE_MEDIUM = 0.25
EFFECT_SIZE_LARGE = 0.40

# Maximum iterations for a-priori binary/linear search
# [REA] FDist-Cdf convergence error strings found at 0x001c3710-0x001c3780
_MAX_N_SEARCH = 10_000_000


# ---------------------------------------------------------------------------
# Input / Output data classes
# ---------------------------------------------------------------------------

@dataclass
class APrioriResult:
    """Result of an a-priori (compute N) analysis."""
    n_total: int
    n_per_group: int          # ceil(N / k); N might not be divisible by k
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


# ---------------------------------------------------------------------------
# Core formula helpers
# ---------------------------------------------------------------------------

def _ncp(f: float, n_total: int) -> float:
    """
    Noncentrality parameter lambda = f^2 * N.
    [DOK] G*Power manual eq. (1) for one-way ANOVA.
    """
    return f * f * n_total


def _critical_f(alpha: float, df1: int, df2: int) -> float:
    """
    Upper-tail critical value: F such that P(F_{df1,df2} > F) = alpha.
    Uses scipy.stats.f.ppf (percent-point function = quantile).
    [DOK] G*Power output field: 'Critical F'
    """
    return float(fdist.ppf(1.0 - alpha, df1, df2))


def _achieved_power(f_crit: float, df1: int, df2: int, lam: float) -> float:
    """
    1 - P(ncF_{df1,df2,lambda} <= F_crit)
    = P(ncF > F_crit)   [upper-tail probability]
    [DOK] G*Power output field: 'Actual power'
    """
    return float(ncf.sf(f_crit, df1, df2, lam))


# ---------------------------------------------------------------------------
# A-priori: find smallest N such that achieved power >= target_power
# ---------------------------------------------------------------------------

def a_priori(
    f: float,
    alpha: float,
    power: float,
    k: int,
) -> APrioriResult:
    """
    Compute the minimum total sample size N for one-way ANOVA.

    Parameters
    ----------
    f      : Cohen's f effect size (> 0)
    alpha  : Type I error rate (0 < alpha < 1)
    power  : Target power (0 < power < 1)
    k      : Number of groups (>= 2)

    Returns
    -------
    APrioriResult with exact N (ceiling), actual power, critical F, df1, df2, ncp.

    [REA] 0x001c8ae4 string 'ANOVA: Fixed effects, omnibus, one-way' confirms
          this is the test registered under F-tests in GPowerNT.exe.
    [REA] 0x001c5594 'There must be at least 2 groups.' — lower bound k >= 2.
    [REA] 0x001c3710 'FDist-Cdf: answer below lower search bound' — G*Power
          detects when N is too small for the search to converge.
    """
    _validate_inputs(f=f, alpha=alpha, power=power, k=k)

    df1 = k - 1

    # G*Power assumes EQUAL group sizes and searches n_per_group.
    # Total sample size is always N = k * n_per_group (a multiple of k).
    # [AJAN] This equal-group hypothesis comes from behavioral analysis; will be
    #        confirmed by differential testing against G*Power oracle values.
    # [REA] 0x001c8ae4 'ANOVA: Fixed effects, omnibus, one-way' — one-way variant.
    # [REA] 0x001c8a8e confirms (groups + covariates) < sample size constraint.
    # Minimum n_per_group = 2 so df2 = N - k = k*(n-1) >= k >= 2.
    n_per_group = 2
    while n_per_group * k <= _MAX_N_SEARCH:
        n = n_per_group * k          # total sample size — always a multiple of k
        df2 = n - k                  # = k * (n_per_group - 1)
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
        f"Could not reach target power {power} within N={_MAX_N_SEARCH}. "
        "Check effect size and alpha."
    )


# ---------------------------------------------------------------------------
# Post-hoc: compute achieved power for given N
# ---------------------------------------------------------------------------

def post_hoc(
    f: float,
    alpha: float,
    n_total: int,
    k: int,
) -> PostHocResult:
    """
    Compute achieved power for a given total sample size.

    Parameters
    ----------
    f       : Cohen's f effect size (> 0)
    alpha   : Type I error rate (0 < alpha < 1)
    n_total : Total sample size (>= k + 1)
    k       : Number of groups (>= 2)
    """
    _validate_inputs(f=f, alpha=alpha, n_total=n_total, k=k)

    df1 = k - 1
    df2 = n_total - k
    lam = _ncp(f, n_total)
    f_crit = _critical_f(alpha, df1, df2)
    pwr = _achieved_power(f_crit, df1, df2, lam)

    return PostHocResult(
        actual_power=pwr,
        critical_f=f_crit,
        df1=df1,
        df2=df2,
        ncp=lam,
    )


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def _validate_inputs(
    f: float | None = None,
    alpha: float | None = None,
    power: float | None = None,
    n_total: int | None = None,
    k: int | None = None,
) -> None:
    """
    Validate analysis inputs and raise ValueError with a descriptive message.
    [REA] Error string 0x001c5140 'Noncentrality parameter ' (partial)
    [REA] Error strings 0x001c5090-0x001c52a1 cover group count validation.
    [REA] 0x001c5594: 'There must be at least 2 groups.'
    """
    errors: list[str] = []

    if f is not None:
        if not math.isfinite(f) or f <= 0:
            errors.append(f"Effect size f must be > 0, got {f}")

    if alpha is not None:
        if not math.isfinite(alpha) or not (0 < alpha < 1):
            errors.append(f"Alpha must be in (0, 1), got {alpha}")

    if power is not None:
        if not math.isfinite(power) or not (0 < power < 1):
            errors.append(f"Power must be in (0, 1), got {power}")
        if alpha is not None and power <= alpha:
            errors.append(
                f"Power ({power}) must be greater than alpha ({alpha})"
            )

    if k is not None:
        if not isinstance(k, int) or k < 2:
            errors.append(f"Number of groups k must be integer >= 2, got {k}")

    if n_total is not None:
        if not isinstance(n_total, int) or n_total < 1:
            errors.append(f"Total sample size must be integer >= 1, got {n_total}")
        if k is not None and n_total <= k:
            errors.append(
                f"Total sample size ({n_total}) must be > k ({k}) so df2 >= 1"
            )

    if errors:
        raise ValueError("; ".join(errors))
