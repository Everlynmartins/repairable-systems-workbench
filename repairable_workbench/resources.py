from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

import numpy as np

from .i18n import tt
from .math_core import poisson_ordered_times, nhpp_failure_terminated_times
from .results import build_summary_text


class ResourceMixin:
    def refresh_stats_window(self):
        if self.stats_window and self.stats_window.winfo_exists() and self.current_result is not None:
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", build_summary_text(self.current_result, self.lang()))
            self.stats_window.title(tt(self.lang(), "stats_title"))

    def open_stats_window(self):
        lang = self.lang()
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.lift()
            self.refresh_stats_window()
            return

        win = tk.Toplevel(self)
        win.title(tt(lang, "stats_title"))
        win.geometry("760x670")

        text = tk.Text(win, wrap="word", font=("Consolas", 10))
        text.pack(fill="both", expand=True)

        self.stats_window = win
        self.stats_text = text
        self.refresh_stats_window()

    def pick_obs_color(self):
        color = colorchooser.askcolor(initialcolor=self.obs_color, title=tt(self.lang(), "pick_obs_color"))[1]
        if color:
            self.obs_color = color
            self.update_plot()

    def pick_model_color(self):
        color = colorchooser.askcolor(initialcolor=self.model_color, title=tt(self.lang(), "pick_model_color"))[1]
        if color:
            self.model_color = color
            self.update_plot()

    def pick_band_color(self):
        color = colorchooser.askcolor(initialcolor=self.band_color, title=tt(self.lang(), "pick_band_color"))[1]
        if color:
            self.band_color = color
            self.update_plot()

    def save_plot_png(self):
        lang = self.lang()
        if self.current_result is None:
            messagebox.showwarning(tt(lang, "warn_save_plot_title"), tt(lang, "warn_save_plot_msg"))
            return

        path = filedialog.asksaveasfilename(
            title=tt(lang, "menu_save_plot"),
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if not path:
            return

        self.figure.savefig(path, dpi=160, bbox_inches="tight")
        self.status_var.set(path)

    def export_stats(self):
        lang = self.lang()
        if self.current_result is None:
            messagebox.showwarning(tt(lang, "warn_export_title"), tt(lang, "warn_export_msg"))
            return

        path = filedialog.asksaveasfilename(
            title=tt(lang, "menu_export_stats"),
            defaultextension=".txt",
            filetypes=[("TXT", "*.txt")],
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(build_summary_text(self.current_result, lang))

        self.status_var.set(path)

    def _synthetic_single_rows(self):
        rng = np.random.default_rng(101)
        times = nhpp_failure_terminated_times(n_fail=22, lam=0.095, beta=0.78, rng=rng)
        times = np.round(times, 3)
        return [[i + 1, float(t)] for i, t in enumerate(times)], times

    def _synthetic_same_rows(self):
        rng = np.random.default_rng(202)
        items = ["A", "B", "C", "D", "E"]
        t_end = 1850.0
        beta = 0.92
        lam = 0.0021
        rows = []
        for item in items:
            times = poisson_ordered_times(lam * (t_end ** beta), beta, t_end, rng)
            for idx, t in enumerate(np.round(times, 3), start=1):
                rows.append([item, idx, float(t)])
        rows.sort(key=lambda r: (r[0], r[2]))
        return rows

    def _synthetic_diff_rows(self):
        rng = np.random.default_rng(303)
        item_end_times = {"A": 4200.0, "B": 2700.0}
        beta = 0.83
        lam = 0.0047
        rows = []
        for item, t_end in item_end_times.items():
            times = poisson_ordered_times(lam * (t_end ** beta), beta, t_end, rng)
            for idx, t in enumerate(np.round(times, 3), start=1):
                rows.append([item, idx, float(t)])
        rows.sort(key=lambda r: (r[0], r[2]))
        aux = [[k, float(v)] for k, v in item_end_times.items()]
        return rows, aux

    def _synthetic_grouped_rows(self):
        rng = np.random.default_rng(404)
        intervals = [(0.0, 2.0), (2.0, 3.0), (3.0, 4.2), (4.2, 5.5), (5.5, 6.8), (6.8, 8.2), (8.2, 9.7), (9.7, 11.0)]
        beta = 0.86
        lam = 3.9
        rows = []
        for a, b in intervals:
            mean = lam * (b ** beta - max(a, 0.0) ** beta)
            n_i = int(rng.poisson(mean))
            rows.append([a, b, n_i])
        return rows

    def load_example(self):
        case = self.case_var.get()

        if case == "single":
            self.term_var.set("failure")
            rows, times = self._synthetic_single_rows()
            self.table_main.set_rows(rows)
            self.t_eval_var.set("450")
            self.t_end_var.set(str(round(float(times[-1]) * 1.1, 3)))

        elif case == "same":
            self.k_var.set("5")
            self.t_end_var.set("1850")
            self.t_eval_var.set("1000")
            self.table_main.set_rows(self._synthetic_same_rows())

        elif case == "diff":
            self.t_eval_var.set("3000")
            rows, aux = self._synthetic_diff_rows()
            self.table_main.set_rows(rows)
            self.table_aux.set_rows(aux)

        elif case == "grouped":
            self.t_eval_var.set("11")
            self.table_main.set_rows(self._synthetic_grouped_rows())

        self.run_analysis()

    def copy_stats_to_clipboard(self):
        if self.current_result is None:
            return
        self.clipboard_clear()
        self.clipboard_append(build_summary_text(self.current_result, self.lang()))
        self.update()
