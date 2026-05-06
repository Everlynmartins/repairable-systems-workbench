from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .i18n import tt
from .math_core import make_model_grid, ttt_coordinates
from .results import AnalysisResult, resolve_text


class PlotMixin:
    def apply_mpl_style(self):
        style_name = self.plot_style_var.get()
        try:
            plt.style.use(style_name if style_name != "default" else "default")
        except Exception:
            plt.style.use("default")

    def update_plot(self):
        lang = self.lang()
        self.ax.clear()
        self.apply_mpl_style()

        if self.show_grid_var.get():
            self.ax.grid(True, alpha=0.25)

        result = self.current_result
        if result is None:
            self.ax.text(0.5, 0.5, tt(lang, "no_analysis"), ha="center", va="center", transform=self.ax.transAxes, fontsize=14)
            self.canvas_plot.draw_idle()
            return

        lw = float(self.linewidth_var.get()) if self.linewidth_var.get().strip() else 2.0
        plot_id = self.plot_id

        if plot_id == "accum":
            self.plot_accumulated(result, loglog=False, lw=lw)
        elif plot_id == "accum_loglog":
            self.plot_accumulated(result, loglog=True, lw=lw)
        elif plot_id == "qq":
            self.plot_qq(result, lw=lw)
        elif plot_id == "ttt":
            self.plot_ttt(result, lw=lw)
        elif plot_id == "intensity":
            self.plot_intensity(result, lw=lw)

        self.figure.tight_layout()
        self.canvas_plot.draw_idle()

    def plot_accumulated(self, result: AnalysisResult, loglog: bool, lw: float):
        lang = self.lang()
        ax = self.ax

        if result.case_name in {"single", "same", "diff"}:
            x = result.times
            y = result.cum_counts
        else:
            x = result.grouped_endpoints
            y = result.grouped_cumulative

        if self.show_points_var.get():
            ax.plot(x, y, linestyle="", marker=self.obs_marker_var.get(), color=self.obs_color, label=tt(lang, "legend_data"))
            ax.step(x, y, where="post", color=self.obs_color, alpha=0.55)

        if self.show_model_var.get():
            grid = make_model_grid(result)
            model = result.lambda_hat * (grid ** result.beta_hat)
            ax.plot(grid, model, self.model_linestyle_var.get(), color=self.model_color, lw=lw, label=tt(lang, "legend_model"))

            if self.show_band_var.get() and result.bootstrap and result.bootstrap.model_grid is not None:
                ax.fill_between(
                    result.bootstrap.model_grid,
                    result.bootstrap.model_band_lower,
                    result.bootstrap.model_band_upper,
                    color=self.band_color,
                    alpha=0.25,
                    label=tt(lang, "legend_band"),
                )

        ax.set_xlabel(tt(lang, "x_accum_time"))
        ax.set_ylabel(tt(lang, "y_cum_failures"))
        ax.set_title(tt(lang, "title_accum"))

        if loglog:
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_title(tt(lang, "title_accum_loglog"))

        ax.legend(loc="best")

    def plot_qq(self, result: AnalysisResult, lw: float):
        lang = self.lang()
        ax = self.ax
        x = result.expected_for_qq_x
        y = result.expected_for_qq_y

        if x.size == 0 or y.size == 0:
            ax.text(0.5, 0.5, tt(lang, "plot_unavailable"), ha="center", va="center", transform=ax.transAxes)
            return

        ax.plot(x, y, linestyle="", marker=self.obs_marker_var.get(), color=self.obs_color)
        lim = max(float(np.max(x)), float(np.max(y))) * 1.05
        ax.plot([0, lim], [0, lim], color=self.model_color, linestyle=self.model_linestyle_var.get(), lw=lw, label=tt(lang, "legend_identity"))
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_xlabel(resolve_text(lang, result.qq_xlabel))
        ax.set_ylabel(resolve_text(lang, result.qq_ylabel))
        ax.set_title(tt(lang, "title_qq"))
        ax.legend(loc="best")

    def plot_ttt(self, result: AnalysisResult, lw: float):
        lang = self.lang()
        ax = self.ax
        if result.case_name not in {"single", "same", "diff"}:
            ax.text(0.5, 0.5, tt(lang, "ttt_individual_only"), ha="center", va="center", transform=ax.transAxes)
            return

        inter = np.diff(np.concatenate(([0.0], result.times)))
        px, py = ttt_coordinates(inter)

        if px.size == 0:
            ax.text(0.5, 0.5, tt(lang, "ttt_unavailable"), ha="center", va="center", transform=ax.transAxes)
            return

        ax.plot(px, py, marker=self.obs_marker_var.get(), color=self.obs_color, lw=lw)
        ax.plot(
            [0, 1],
            [0, 1],
            linestyle=self.model_linestyle_var.get(),
            color=self.model_color,
            lw=lw,
            label=tt(lang, "legend_identity"),
        )
        ax.set_xlabel(tt(lang, "x_fraction"))
        ax.set_ylabel(tt(lang, "y_ttt"))
        ax.set_title(tt(lang, "title_ttt"))
        ax.legend(loc="best")

    def plot_intensity(self, result: AnalysisResult, lw: float):
        lang = self.lang()
        ax = self.ax
        grid = make_model_grid(result)
        z = result.lambda_hat * result.beta_hat * (grid ** (result.beta_hat - 1))
        ax.plot(
            grid,
            z,
            color=self.model_color,
            linestyle=self.model_linestyle_var.get(),
            lw=lw,
            label=tt(lang, "legend_model"),
        )
        ax.scatter(
            [result.t_eval],
            [result.z_hat],
            color=self.obs_color,
            marker=self.obs_marker_var.get(),
            s=70,
            zorder=5,
            label=f"{tt(lang, 'summary_z')}({result.t_eval:.3g})",
        )

        if self.show_band_var.get() and result.bootstrap and result.bootstrap.reps_ok > 0:
            z_stack = []
            for lam, beta in zip(result.bootstrap.lambda_samples, result.bootstrap.beta_samples):
                if beta > 0:
                    z_stack.append(lam * beta * (grid ** (beta - 1)))
            if len(z_stack) > 0:
                z_stack = np.asarray(z_stack)
                ax.fill_between(
                    grid,
                    np.quantile(z_stack, 0.05, axis=0),
                    np.quantile(z_stack, 0.95, axis=0),
                    color=self.band_color,
                    alpha=0.25,
                    label=tt(lang, "legend_band"),
                )

        ax.set_xlabel(tt(lang, "x_time"))
        ax.set_ylabel(tt(lang, "y_intensity"))
        ax.set_title(tt(lang, "title_intensity"))
        ax.legend(loc="best")
