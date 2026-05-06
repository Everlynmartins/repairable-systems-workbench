from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from .i18n import TEXTS, tt


@dataclass
class BootstrapBundle:
    beta_samples: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    lambda_samples: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    z_samples: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    model_band_lower: Optional[np.ndarray] = None
    model_band_upper: Optional[np.ndarray] = None
    model_grid: Optional[np.ndarray] = None
    reps_ok: int = 0
    note: str = ""


@dataclass
class AnalysisResult:
    case_name: str
    termination: str
    n_failures: int
    beta_hat: float
    lambda_hat: float
    z_hat: float
    t_eval: float
    times: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    cum_counts: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    grouped_endpoints: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    grouped_counts: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    grouped_cumulative: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    k_items: Optional[int] = None
    t_end: Optional[float] = None
    gof_name: str = ""
    gof_stat: Optional[float] = None
    gof_crit: Optional[float] = None
    gof_df: Optional[int] = None
    gof_accept: Optional[bool] = None
    exact_beta_ci: Optional[Tuple[float, float]] = None
    exact_z_ci: Optional[Tuple[float, float]] = None
    bootstrap_ci_beta: Optional[Tuple[float, float]] = None
    bootstrap_ci_lambda: Optional[Tuple[float, float]] = None
    bootstrap_ci_z: Optional[Tuple[float, float]] = None
    expected_for_qq_x: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    expected_for_qq_y: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    qq_xlabel: str = ""
    qq_ylabel: str = ""
    messages: List[str] = field(default_factory=list)
    bootstrap: Optional[BootstrapBundle] = None


def resolve_text(lang: str, value: Optional[str]) -> str:
    if value is None:
        return ""
    return tt(lang, value) if value in TEXTS.get(lang, {}) or value in TEXTS["en"] else str(value)


def data_type_text(lang: str, case_name: str) -> str:
    mapping = {
        "single": "data_type_single",
        "same": "data_type_same",
        "diff": "data_type_diff",
        "grouped": "data_type_grouped",
    }
    return tt(lang, mapping.get(case_name, case_name))


def termination_text(lang: str, termination: str) -> str:
    mapping = {
        "time": "term_time",
        "failure": "term_failure",
        "grouped": "term_grouped",
    }
    return tt(lang, mapping.get(termination, termination))


def gof_text(lang: str, gof_name: str) -> str:
    mapping = {
        "cvm": "gof_cvm",
        "chi2": "gof_chi2",
    }
    return tt(lang, mapping.get(gof_name, gof_name))


def build_summary_text(result: AnalysisResult, lang: str) -> str:
    lines = []
    lines.append(f"{tt(lang, 'summary_data_type')}: {data_type_text(lang, result.case_name)}")
    lines.append(f"{tt(lang, 'summary_termination')}: {termination_text(lang, result.termination)}")
    lines.append(f"{tt(lang, 'summary_n_failures')}: {result.n_failures}")
    if result.k_items is not None:
        lines.append(f"{tt(lang, 'summary_k_items')}: {result.k_items}")
    if result.t_end is not None:
        lines.append(f"{tt(lang, 'summary_horizon')}: {result.t_end:.8g}")

    lines.append("")
    lines.append(tt(lang, "summary_estimates"))
    lines.append(f"{tt(lang, 'summary_beta')} = {result.beta_hat:.10g}")
    lines.append(f"{tt(lang, 'summary_lambda')} = {result.lambda_hat:.10g}")
    lines.append(f"{tt(lang, 'summary_z')}({result.t_eval:.10g}) = {result.z_hat:.10g}")

    if result.exact_beta_ci is not None:
        lines.append(f"{tt(lang, 'summary_ci_beta_exact')} = ({result.exact_beta_ci[0]:.10g}, {result.exact_beta_ci[1]:.10g})")
    if result.exact_z_ci is not None:
        lines.append(f"{tt(lang, 'summary_ci_z_exact')} = ({result.exact_z_ci[0]:.10g}, {result.exact_z_ci[1]:.10g})")
    if result.bootstrap_ci_beta is not None:
        lines.append(f"{tt(lang, 'summary_ci_beta_boot')} = ({result.bootstrap_ci_beta[0]:.10g}, {result.bootstrap_ci_beta[1]:.10g})")
    if result.bootstrap_ci_lambda is not None:
        lines.append(f"{tt(lang, 'summary_ci_lambda_boot')} = ({result.bootstrap_ci_lambda[0]:.10g}, {result.bootstrap_ci_lambda[1]:.10g})")
    if result.bootstrap_ci_z is not None:
        lines.append(f"{tt(lang, 'summary_ci_z_boot')} = ({result.bootstrap_ci_z[0]:.10g}, {result.bootstrap_ci_z[1]:.10g})")

    if result.gof_name:
        lines.append("")
        lines.append(tt(lang, "summary_gof"))
        lines.append(f"{tt(lang, 'summary_test')}: {gof_text(lang, result.gof_name)}")
        if result.gof_stat is not None:
            lines.append(f"{tt(lang, 'summary_stat')}: {result.gof_stat:.10g}")
        if result.gof_crit is not None:
            lines.append(f"{tt(lang, 'summary_crit')}: {result.gof_crit:.10g}")
        if result.gof_df is not None:
            lines.append(f"{tt(lang, 'summary_df')}: {result.gof_df}")
        if result.gof_accept is not None:
            conclusion = tt(lang, "conclusion_accept") if result.gof_accept else tt(lang, "conclusion_reject")
            lines.append(f"{tt(lang, 'summary_conclusion')}: {conclusion}")

    if result.messages:
        lines.append("")
        lines.append(tt(lang, "summary_messages"))
        for msg in result.messages:
            lines.append(f"• {resolve_text(lang, msg)}")

    if result.bootstrap and result.bootstrap.note:
        lines.append("")
        lines.append(tt(lang, "summary_bootstrap"))
        if result.bootstrap.note == "none":
            lines.append(tt(lang, "msg_bootstrap_failed"))
        else:
            lines.append(result.bootstrap.note)

    return "\n".join(lines)
