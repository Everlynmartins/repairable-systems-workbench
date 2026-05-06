from __future__ import annotations

import math
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import root_scalar, minimize_scalar
from scipy.stats import chi2 as chi2_dist

from .results import AnalysisResult, BootstrapBundle


def safe_float(x: Any) -> float:
    s = str(x).strip().replace(",", ".")
    if s == "":
        raise ValueError("empty")
    return float(s)


def sort_positive_times(times: Sequence[float]) -> np.ndarray:
    arr = np.asarray(times, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return arr
    if np.any(arr <= 0):
        raise ValueError("nonpositive")
    return np.sort(arr)


def solve_positive_root(func, lo: float = 1e-4, hi: float = 10.0) -> float:
    flo = func(lo)
    fhi = func(hi)
    for _ in range(32):
        if np.isfinite(flo) and np.isfinite(fhi) and flo * fhi < 0:
            sol = root_scalar(func, bracket=[lo, hi], method="brentq")
            return float(sol.root)
        hi *= 1.8
        fhi = func(hi)
        if lo > 1e-12:
            lo /= 1.5
            flo = func(lo)

    def objective(xlog: float) -> float:
        beta = math.exp(xlog)
        v = func(beta)
        if not np.isfinite(v):
            return 1e100
        return abs(v)

    res = minimize_scalar(objective, bounds=(-12, 12), method="bounded")
    beta = math.exp(float(res.x))
    if not np.isfinite(func(beta)):
        raise ValueError("root")
    return beta


def poisson_ordered_times(mean_n: float, beta: float, t_end: float, rng: np.random.Generator) -> np.ndarray:
    n = int(rng.poisson(mean_n))
    if n <= 0:
        return np.array([], dtype=float)
    u = np.sort(rng.uniform(size=n))
    return t_end * np.power(u, 1.0 / beta)


def nhpp_failure_terminated_times(n_fail: int, lam: float, beta: float, rng: np.random.Generator) -> np.ndarray:
    exp_samples = rng.exponential(scale=1.0, size=n_fail)
    gamma_arrivals = np.cumsum(exp_samples)
    return np.power(gamma_arrivals / lam, 1.0 / beta)


def ttt_coordinates(interarrivals: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    x = np.sort(np.asarray(interarrivals, dtype=float))
    x = x[x > 0]
    n = len(x)
    if n == 0:
        return np.array([]), np.array([])
    s = np.sum(x)
    px = np.arange(0, n + 1) / n
    py = [0.0]
    for r in range(1, n + 1):
        partial = np.sum(x[:r])
        if r < n:
            y = (partial + (n - r) * x[r - 1]) / s
        else:
            y = 1.0
        py.append(float(y))
    return px, np.asarray(py)


def cvm_statistic_from_u(u_sorted: np.ndarray) -> float:
    """Modified Cramér von Mises statistic for the PLP fit test.

    The input must already be transformed with the fitted shape
    parameter, that is u_j = (t_j / T) ** beta_hat, sorted increasingly.
    """
    m = len(u_sorted)
    if m < 1:
        return float("nan")
    centers = (2 * np.arange(1, m + 1) - 1) / (2 * m)
    return float((1 / (12 * m)) + np.sum((u_sorted - centers) ** 2))


def quantile_type8(values: np.ndarray, probability: float) -> float:
    """R quantile type 8 equivalent when the NumPy version supports it."""
    try:
        return float(np.quantile(values, probability, method="median_unbiased"))
    except TypeError:
        return float(np.quantile(values, probability))


@lru_cache(maxsize=256)
def cvm_critical_value(
    m: int,
    alpha: float = 0.10,
    reps: int = 15000,
    seed: int = 123,
    batch_size: int = 50000,
) -> float:
    """Monte Carlo critical value for the modified PLP Cramér von Mises test.

    This computes the critical value algorithmically and does not use any
    embedded critical value table. The simulation follows the standard
    PLP construction: generate ordered Uniform(0, 1) samples, estimate the
    relative shape in each sample, transform the ordered uniforms with that
    estimate, compute C2, then return the empirical quantile 1 minus alpha.
    """
    m = int(m)
    reps = int(reps)
    batch_size = int(batch_size)

    if m < 2:
        return float("nan")
    if not (0.0 < float(alpha) < 1.0):
        return float("nan")
    if reps < 1000:
        reps = 1000
    if batch_size < 1:
        batch_size = reps

    rng = np.random.default_rng(int(seed))
    centers = (2 * np.arange(1, m + 1) - 1) / (2 * m)
    c2 = np.empty(reps, dtype=float)

    pos = 0
    while pos < reps:
        b = min(batch_size, reps - pos)
        u = rng.random((b, m))
        u.sort(axis=1)

        beta_rel = (m - 1) / np.sum(np.log(1.0 / u), axis=1)
        z = u ** beta_rel[:, None]
        d = z - centers[None, :]
        c2[pos:pos + b] = (1.0 / (12 * m)) + np.sum(d ** 2, axis=1)
        pos += b

    return quantile_type8(c2, 1.0 - float(alpha))


def approx_z_multipliers(n: int, termination: str) -> tuple[float, float]:
    """
    Analytical large-sample approximation for multiplicative limits of z(t).
    Used for every n to avoid embedded tabulations.
    """
    zq = 1.6448536269514722  # 90% two-sided interval
    if termination == "time":
        base = max(((n - 1) / n), 1e-12)
        lower = (base * (1 + zq / math.sqrt(max(2 * n, 1e-12)))) ** -2
        upper = (base * (1 - zq / math.sqrt(max(2 * n, 1e-12)))) ** -2
        return lower, upper
    base = max(((n - 2) / n), 1e-12)
    lower = (base * (1 + zq * math.sqrt(2 / max(n, 1e-12)))) ** -1
    upper = (base * (1 - zq * math.sqrt(2 / max(n, 1e-12)))) ** -1
    return lower, upper


def exact_beta_ci_case1(beta_hat: float, n: int, termination: str) -> Tuple[float, float]:
    if termination == "time":
        dl = float(chi2_dist.ppf(0.05, 2 * n) / (2 * (n - 1)))
        du = float(chi2_dist.ppf(0.95, 2 * n) / (2 * (n - 1)))
    else:
        dl = float(chi2_dist.ppf(0.05, 2 * (n - 1)) / (2 * (n - 2)))
        du = float(chi2_dist.ppf(0.95, 2 * (n - 1)) / (2 * (n - 2)))
    return dl * beta_hat, du * beta_hat


def exact_z_ci_case1(z_hat: float, n: int, termination: str) -> Tuple[float, float]:
    l, u = approx_z_multipliers(n, termination)
    return z_hat / u, z_hat / l


def combine_small_expected(starts, ends, counts, expected):
    rows = [(float(a), float(b), int(n), float(e)) for a, b, n, e in zip(starts, ends, counts, expected)]
    combined = []
    buffer_row = None
    for row in rows:
        if buffer_row is None:
            buffer_row = list(row)
        else:
            if buffer_row[3] < 5:
                buffer_row[1] = row[1]
                buffer_row[2] += row[2]
                buffer_row[3] += row[3]
            else:
                combined.append(tuple(buffer_row))
                buffer_row = list(row)
    if buffer_row is not None:
        if buffer_row[3] < 5 and combined:
            prev = list(combined[-1])
            prev[1] = buffer_row[1]
            prev[2] += buffer_row[2]
            prev[3] += buffer_row[3]
            combined[-1] = tuple(prev)
        else:
            combined.append(tuple(buffer_row))
    return combined


def fit_case_single(
    times: Sequence[float],
    termination: str,
    t_end: Optional[float] = None,
    t_eval: Optional[float] = None,
    messages: Optional[List[str]] = None,
) -> AnalysisResult:
    times = sort_positive_times(times)
    n = len(times)
    if n < 3:
        raise ValueError("single")

    if termination == "time":
        if t_end is None:
            raise ValueError("horizon")
        if t_end <= float(times[-1]):
            raise ValueError("horizon")
        s = float(np.sum(np.log(t_end / times)))
        beta = (n - 1) / s
        lam = n / (t_end ** beta)
        t_gof = t_end
        m = n
        gof_times = times
    elif termination == "failure":
        t_end = float(times[-1])
        s = float(np.sum(np.log(t_end / times)))
        beta = (n - 2) / s
        lam = n / (t_end ** beta)
        t_gof = t_end
        m = n - 1
        gof_times = times[:-1]
    else:
        raise ValueError("termination")

    if t_eval is None:
        t_eval = t_end
    z_hat = lam * beta * (t_eval ** (beta - 1))
    u = np.sort((gof_times / t_gof) ** beta)
    c2 = cvm_statistic_from_u(u)
    crit = cvm_critical_value(m, alpha=0.10)
    accept = c2 <= crit
    expected = (np.arange(1, n + 1) / lam) ** (1 / beta)

    return AnalysisResult(
        case_name="single",
        termination=termination,
        n_failures=n,
        beta_hat=beta,
        lambda_hat=lam,
        z_hat=z_hat,
        t_eval=float(t_eval),
        times=times,
        cum_counts=np.arange(1, n + 1),
        t_end=float(t_end),
        gof_name="cvm",
        gof_stat=c2,
        gof_crit=crit,
        gof_accept=accept,
        exact_beta_ci=exact_beta_ci_case1(beta, n, termination),
        exact_z_ci=exact_z_ci_case1(z_hat, n, termination),
        expected_for_qq_x=times,
        expected_for_qq_y=expected,
        qq_xlabel="x_observed_time",
        qq_ylabel="y_expected_time",
        messages=messages or [],
    )


def fit_case_same(
    item_times: Sequence[Tuple[str, float]],
    k_items: int,
    t_end: float,
    t_eval: Optional[float] = None,
    messages: Optional[List[str]] = None,
) -> AnalysisResult:
    if k_items < 1:
        raise ValueError("k")
    times = sort_positive_times([t for _, t in item_times])
    n = len(times)
    if n < 3:
        raise ValueError("same")
    if t_end <= float(times[-1]):
        raise ValueError("horizon")

    s = float(np.sum(np.log(t_end / times)))
    beta = (n - 1) / s
    lam = n / (k_items * (t_end ** beta))

    if t_eval is None:
        t_eval = t_end
    z_hat = lam * beta * (t_eval ** (beta - 1))

    m = n
    u = np.sort((times / t_end) ** beta)
    c2 = cvm_statistic_from_u(u)
    crit = cvm_critical_value(m, alpha=0.10)
    accept = c2 <= crit
    expected = (np.arange(1, n + 1) / (k_items * lam)) ** (1 / beta)

    return AnalysisResult(
        case_name="same",
        termination="time",
        n_failures=n,
        beta_hat=beta,
        lambda_hat=lam,
        z_hat=z_hat,
        t_eval=float(t_eval),
        times=times,
        cum_counts=np.arange(1, n + 1),
        k_items=k_items,
        t_end=float(t_end),
        gof_name="cvm",
        gof_stat=c2,
        gof_crit=crit,
        gof_accept=accept,
        exact_beta_ci=exact_beta_ci_case1(beta, n, "time"),
        exact_z_ci=exact_z_ci_case1(z_hat, n, "time"),
        expected_for_qq_x=times,
        expected_for_qq_y=expected,
        qq_xlabel="x_observed_time",
        qq_ylabel="y_expected_time",
        messages=messages or [],
    )


def fit_case_diff(
    item_times: Sequence[Tuple[str, float]],
    item_end_times: Dict[str, float],
    t_eval: Optional[float] = None,
    messages: Optional[List[str]] = None,
) -> AnalysisResult:
    all_times = []
    for item, t in item_times:
        if item not in item_end_times:
            raise ValueError("field_end_obs")
        if t <= 0 or t > item_end_times[item]:
            raise ValueError("diff")
        all_times.append(float(t))

    times = sort_positive_times(all_times)
    n = len(times)
    if n < 3:
        raise ValueError("diff")

    end_times = np.array([float(v) for _, v in sorted(item_end_times.items())], dtype=float)
    if np.any(end_times <= 0):
        raise ValueError("field_end_obs")

    sum_logs = float(np.sum(np.log(times)))

    def func(beta: float) -> float:
        num = np.sum((end_times ** beta) * np.log(end_times))
        den = np.sum(end_times ** beta)
        return n / beta + sum_logs - n * num / den

    beta = solve_positive_root(func)
    lam = n / float(np.sum(end_times ** beta))

    if t_eval is None:
        t_eval = float(np.max(end_times))
    z_hat = lam * beta * (t_eval ** (beta - 1))

    m = n
    t_gof = float(np.max(end_times))
    u = np.sort((times / t_gof) ** beta)
    c2 = cvm_statistic_from_u(u)
    crit = cvm_critical_value(m, alpha=0.10)
    accept = c2 <= crit
    expected = (np.arange(1, n + 1) / lam) ** (1 / beta)

    msg = list(messages or [])
    return AnalysisResult(
        case_name="diff",
        termination="time",
        n_failures=n,
        beta_hat=beta,
        lambda_hat=lam,
        z_hat=z_hat,
        t_eval=float(t_eval),
        times=times,
        cum_counts=np.arange(1, n + 1),
        k_items=len(item_end_times),
        t_end=float(np.max(end_times)),
        gof_name="cvm",
        gof_stat=c2,
        gof_crit=crit,
        gof_accept=accept,
        exact_beta_ci=exact_beta_ci_case1(beta, n, "time"),
        exact_z_ci=exact_z_ci_case1(z_hat, n, "time"),
        expected_for_qq_x=times,
        expected_for_qq_y=expected,
        qq_xlabel="x_observed_time",
        qq_ylabel="y_expected_time",
        messages=msg,
    )


def fit_case_grouped(
    interval_rows: Sequence[Tuple[float, float, int]],
    t_eval: Optional[float] = None,
    messages: Optional[List[str]] = None,
) -> AnalysisResult:
    rows = sorted([(float(a), float(b), int(n)) for a, b, n in interval_rows], key=lambda x: x[1])
    if len(rows) < 3:
        raise ValueError("grouped")

    starts = np.array([r[0] for r in rows], dtype=float)
    ends = np.array([r[1] for r in rows], dtype=float)
    counts = np.array([r[2] for r in rows], dtype=int)

    if np.any(ends <= starts):
        raise ValueError("grouped")
    if np.any(counts < 0):
        raise ValueError("grouped")

    t_d = float(ends[-1])
    if t_d <= 0:
        raise ValueError("grouped")

    def term(beta: float, a: float, b: float) -> float:
        if a <= 0:
            num = (b ** beta) * math.log(max(b, 1e-300))
            den = b ** beta
            return num / den
        num = (b ** beta) * math.log(b) - (a ** beta) * math.log(a)
        den = (b ** beta) - (a ** beta)
        return num / den

    def func(beta: float) -> float:
        return float(
            np.sum([counts[i] * (term(beta, starts[i], ends[i]) - math.log(t_d)) for i in range(len(rows))])
        )

    beta = solve_positive_root(func)
    n_total = int(np.sum(counts))
    lam = n_total / (t_d ** beta)

    if t_eval is None:
        t_eval = t_d
    z_hat = lam * beta * (t_eval ** (beta - 1))

    expected_interval = lam * (ends ** beta - starts ** beta)
    chi_rows = combine_small_expected(starts, ends, counts, expected_interval)
    d_comb = len(chi_rows)
    chi2_stat = float(np.sum([(n - e) ** 2 / e for _, _, n, e in chi_rows]))
    df = max(d_comb - 2, 1)
    crit = float(chi2_dist.ppf(0.90, df))
    accept = chi2_stat <= crit

    cum_obs = np.cumsum(counts)
    cum_exp = lam * (ends ** beta)

    msg = list(messages or [])
    return AnalysisResult(
        case_name="grouped",
        termination="grouped",
        n_failures=n_total,
        beta_hat=beta,
        lambda_hat=lam,
        z_hat=z_hat,
        t_eval=float(t_eval),
        grouped_endpoints=ends,
        grouped_counts=counts,
        grouped_cumulative=cum_obs,
        t_end=t_d,
        gof_name="chi2",
        gof_stat=chi2_stat,
        gof_crit=crit,
        gof_df=df,
        gof_accept=accept,
        expected_for_qq_x=cum_obs,
        expected_for_qq_y=cum_exp,
        qq_xlabel="x_obs_cum_failures",
        qq_ylabel="y_exp_cum_failures",
        messages=msg,
    )


def make_model_grid(result: AnalysisResult) -> np.ndarray:
    if result.case_name in {"single", "same", "diff"}:
        tmax = result.t_end if result.t_end is not None else float(result.times[-1])
    else:
        tmax = float(result.grouped_endpoints[-1])
    tmin = max(tmax * 1e-4, 1e-6)
    return np.linspace(tmin, tmax, 250)


def bootstrap_analysis(spec: Dict[str, Any], result: AnalysisResult, reps: int = 200, seed: Optional[int] = None) -> BootstrapBundle:
    rng = np.random.default_rng(seed)
    beta_vals = []
    lam_vals = []
    z_vals = []
    t_grid = make_model_grid(result)
    band_stack = []
    failures_ok = 0

    for _ in range(reps):
        try:
            if spec["case"] == "single":
                if spec["termination"] == "time":
                    sim_times = poisson_ordered_times(
                        result.lambda_hat * (spec["t_end"] ** result.beta_hat),
                        result.beta_hat,
                        spec["t_end"],
                        rng,
                    )
                    if len(sim_times) < 3:
                        continue
                    sim_res = fit_case_single(sim_times, "time", t_end=spec["t_end"], t_eval=result.t_eval)
                else:
                    sim_times = nhpp_failure_terminated_times(
                        result.n_failures, result.lambda_hat, result.beta_hat, rng
                    )
                    if len(sim_times) < 3:
                        continue
                    sim_res = fit_case_single(sim_times, "failure", t_eval=result.t_eval)

            elif spec["case"] == "same":
                sim_rows = []
                for j in range(spec["k_items"]):
                    sim_t = poisson_ordered_times(
                        result.lambda_hat * (spec["t_end"] ** result.beta_hat),
                        result.beta_hat,
                        spec["t_end"],
                        rng,
                    )
                    for t in sim_t:
                        sim_rows.append((f"item_{j+1}", float(t)))
                if len(sim_rows) < 3:
                    continue
                sim_res = fit_case_same(sim_rows, spec["k_items"], spec["t_end"], t_eval=result.t_eval)

            elif spec["case"] == "diff":
                sim_rows = []
                item_end_times = spec["item_end_times"]
                for item, t_end in item_end_times.items():
                    sim_t = poisson_ordered_times(
                        result.lambda_hat * (t_end ** result.beta_hat),
                        result.beta_hat,
                        t_end,
                        rng,
                    )
                    for t in sim_t:
                        sim_rows.append((item, float(t)))
                if len(sim_rows) < 3:
                    continue
                sim_res = fit_case_diff(sim_rows, item_end_times, t_eval=result.t_eval)

            elif spec["case"] == "grouped":
                sim_intervals = []
                for a, b, _n in spec["interval_rows"]:
                    mean = result.lambda_hat * (b ** result.beta_hat - a ** result.beta_hat)
                    n_i = int(rng.poisson(mean))
                    sim_intervals.append((a, b, n_i))
                if sum(n for _, _, n in sim_intervals) < 3:
                    continue
                sim_res = fit_case_grouped(sim_intervals, t_eval=result.t_eval)

            else:
                continue

            beta_vals.append(sim_res.beta_hat)
            lam_vals.append(sim_res.lambda_hat)
            z_vals.append(sim_res.z_hat)
            band_stack.append(sim_res.lambda_hat * (t_grid ** sim_res.beta_hat))
            failures_ok += 1

        except Exception:
            continue

    if failures_ok == 0:
        return BootstrapBundle(note="none")

    beta_samples = np.asarray(beta_vals)
    lambda_samples = np.asarray(lam_vals)
    z_samples = np.asarray(z_vals)
    band_stack = np.asarray(band_stack)

    return BootstrapBundle(
        beta_samples=beta_samples,
        lambda_samples=lambda_samples,
        z_samples=z_samples,
        model_grid=t_grid,
        model_band_lower=np.quantile(band_stack, 0.05, axis=0),
        model_band_upper=np.quantile(band_stack, 0.95, axis=0),
        reps_ok=failures_ok,
        note=f"{failures_ok}/{reps}",
    )
