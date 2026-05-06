from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from .i18n import LANG_OPTIONS, PLOT_IDS, tt
from .math_core import bootstrap_analysis, fit_case_diff, fit_case_grouped, fit_case_same, fit_case_single, safe_float
from .results import AnalysisResult
from .ui_components import SpreadsheetEditor, add_help_button
from .plotting import PlotMixin
from .resources import ResourceMixin


class RepairableSystemsWorkbench(PlotMixin, ResourceMixin, tk.Tk):
    def __init__(self):
        super().__init__()

        self.lang_var = tk.StringVar(value="pt")

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.current_result: Optional[AnalysisResult] = None
        self.current_spec: Dict[str, Any] = {}
        self.stats_window = None

        self.case_var = tk.StringVar(value="single")
        self.term_var = tk.StringVar(value="time")
        self.layout_var = tk.StringVar(value="split")
        self.plot_style_var = tk.StringVar(value="default")
        self.bootstrap_var = tk.BooleanVar(value=True)
        self.show_model_var = tk.BooleanVar(value=True)
        self.show_band_var = tk.BooleanVar(value=True)
        self.show_points_var = tk.BooleanVar(value=True)
        self.show_grid_var = tk.BooleanVar(value=True)

        self.plot_id = "accum"
        self.plot_type_display_var = tk.StringVar()

        self.obs_color = "#1f77b4"
        self.model_color = "#d62728"
        self.band_color = "#ff9896"
        self.obs_marker_var = tk.StringVar(value="o")
        self.model_linestyle_var = tk.StringVar(value="--")
        self.linewidth_var = tk.StringVar(value="2.0")

        self.bootstrap_reps_var = tk.StringVar(value="250")
        self.seed_var = tk.StringVar(value="123")
        self.k_var = tk.StringVar(value="5")
        self.t_end_var = tk.StringVar(value="1000")
        self.t_eval_var = tk.StringVar(value="1000")

        self.title(tt(self.lang(), "app_title"))
        self.geometry("1540x950")
        self.minsize(1240, 780)

        self._build_menu()
        self._build_top_area()
        self._build_main_layout()
        self._build_data_area()
        self._build_plot_area()
        self._build_status_bar()

        self._apply_layout()
        self._refresh_case_ui()
        self._apply_language()
        self.load_example()

    def lang(self) -> str:
        return self.lang_var.get()

    def _build_menu(self):
        self.menu_bar = tk.Menu(self, tearoff=0)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(command=self.load_example)
        self.file_menu.add_command(command=self.export_stats)
        self.file_menu.add_separator()
        self.file_menu.add_command(command=self.destroy)
        self.menu_bar.add_cascade(label=tt(self.lang(), "file_menu"), menu=self.file_menu)

        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_radiobutton(variable=self.layout_var, value="table", command=self._apply_layout)
        self.view_menu.add_radiobutton(variable=self.layout_var, value="split", command=self._apply_layout)
        self.view_menu.add_radiobutton(variable=self.layout_var, value="plot", command=self._apply_layout)
        self.menu_bar.add_cascade(label=tt(self.lang(), "view_menu"), menu=self.view_menu)

        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(command=self.run_analysis)
        self.tools_menu.add_command(command=self.open_stats_window)
        self.tools_menu.add_command(command=self.save_plot_png)
        self.menu_bar.add_cascade(label=tt(self.lang(), "tools_menu"), menu=self.tools_menu)

        self.config(menu=self.menu_bar)

    def _build_top_area(self):
        self.top_outer = ttk.Frame(self, padding=8)
        self.top_outer.pack(fill="x")

        lang_row = ttk.Frame(self.top_outer)
        lang_row.pack(fill="x", pady=(0, 6))

        self.lbl_language = ttk.Label(lang_row)
        self.lbl_language.pack(side="left", padx=(0, 6))

        self.cmb_language = ttk.Combobox(
            lang_row,
            state="readonly",
            values=[name for _code, name in LANG_OPTIONS],
            width=16,
        )
        self.cmb_language.pack(side="left")
        self.cmb_language.current(0)
        self.cmb_language.bind("<<ComboboxSelected>>", self._on_language_change)

        help_lang = add_help_button(lang_row, lambda: tt(self.lang(), "help_language"))
        help_lang.pack(side="left", padx=(4, 0))

        self.box_data_type = ttk.LabelFrame(self.top_outer)
        self.box_data_type.pack(fill="x", pady=(0, 6))
        self.data_type_row = ttk.Frame(self.box_data_type)
        self.data_type_row.pack(fill="x", padx=8, pady=8)

        self.rb_single = ttk.Radiobutton(self.data_type_row, variable=self.case_var, value="single", command=self._refresh_case_ui)
        self.rb_same = ttk.Radiobutton(self.data_type_row, variable=self.case_var, value="same", command=self._refresh_case_ui)
        self.rb_diff = ttk.Radiobutton(self.data_type_row, variable=self.case_var, value="diff", command=self._refresh_case_ui)
        self.rb_grouped = ttk.Radiobutton(self.data_type_row, variable=self.case_var, value="grouped", command=self._refresh_case_ui)
        for rb in (self.rb_single, self.rb_same, self.rb_diff, self.rb_grouped):
            rb.pack(side="left", padx=6)

        self.box_params = ttk.LabelFrame(self.top_outer)
        self.box_params.pack(fill="x", pady=(0, 6))
        self.param_grid = ttk.Frame(self.box_params)
        self.param_grid.pack(fill="x", padx=8, pady=8)

        self.lbl_termination = ttk.Label(self.param_grid)
        self.lbl_termination.grid(row=0, column=0, sticky="w", padx=4, pady=3)
        self.help_termination = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_termination"))
        self.help_termination.grid(row=0, column=1, sticky="w", padx=(0, 6), pady=3)

        self.term_wrap = ttk.Frame(self.param_grid)
        self.term_wrap.grid(row=0, column=2, sticky="w", padx=4, pady=3)

        self.rb_term_time = ttk.Radiobutton(self.term_wrap, variable=self.term_var, value="time", command=self._refresh_case_ui)
        self.rb_term_time.pack(side="left")
        self.rb_term_failure = ttk.Radiobutton(self.term_wrap, variable=self.term_var, value="failure", command=self._refresh_case_ui)
        self.rb_term_failure.pack(side="left", padx=(6, 0))

        self.lbl_horizon = ttk.Label(self.param_grid)
        self.lbl_horizon.grid(row=0, column=3, sticky="w", padx=4, pady=3)
        self.help_horizon = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_horizon"))
        self.help_horizon.grid(row=0, column=4, sticky="w", padx=(0, 6), pady=3)
        self.ent_horizon = ttk.Entry(self.param_grid, textvariable=self.t_end_var, width=12)
        self.ent_horizon.grid(row=0, column=5, sticky="w", padx=4, pady=3)

        self.lbl_k_items = ttk.Label(self.param_grid)
        self.lbl_k_items.grid(row=0, column=6, sticky="w", padx=4, pady=3)
        self.help_k_items = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_k_items"))
        self.help_k_items.grid(row=0, column=7, sticky="w", padx=(0, 6), pady=3)
        self.ent_k_items = ttk.Entry(self.param_grid, textvariable=self.k_var, width=10)
        self.ent_k_items.grid(row=0, column=8, sticky="w", padx=4, pady=3)

        self.lbl_z_eval = ttk.Label(self.param_grid)
        self.lbl_z_eval.grid(row=0, column=9, sticky="w", padx=4, pady=3)
        self.help_z_eval = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_z_eval"))
        self.help_z_eval.grid(row=0, column=10, sticky="w", padx=(0, 6), pady=3)
        self.ent_z_eval = ttk.Entry(self.param_grid, textvariable=self.t_eval_var, width=12)
        self.ent_z_eval.grid(row=0, column=11, sticky="w", padx=4, pady=3)

        self.lbl_bootstrap = ttk.Label(self.param_grid)
        self.lbl_bootstrap.grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.help_bootstrap = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_bootstrap_reps"))
        self.help_bootstrap.grid(row=1, column=1, sticky="w", padx=(0, 6), pady=3)
        self.ent_bootstrap = ttk.Entry(self.param_grid, textvariable=self.bootstrap_reps_var, width=10)
        self.ent_bootstrap.grid(row=1, column=2, sticky="w", padx=4, pady=3)

        self.chk_bootstrap = ttk.Checkbutton(self.param_grid, variable=self.bootstrap_var)
        self.chk_bootstrap.grid(row=1, column=3, sticky="w", padx=4, pady=3)
        self.help_bootstrap_ci = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_bootstrap_ci"))
        self.help_bootstrap_ci.grid(row=1, column=4, sticky="w", padx=(0, 6), pady=3)

        self.lbl_seed = ttk.Label(self.param_grid)
        self.lbl_seed.grid(row=1, column=5, sticky="w", padx=4, pady=3)
        self.help_seed = add_help_button(self.param_grid, lambda: tt(self.lang(), "help_seed"))
        self.help_seed.grid(row=1, column=6, sticky="w", padx=(0, 6), pady=3)
        self.ent_seed = ttk.Entry(self.param_grid, textvariable=self.seed_var, width=10)
        self.ent_seed.grid(row=1, column=7, sticky="w", padx=4, pady=3)

        self.box_plot_options = ttk.LabelFrame(self.top_outer)
        self.box_plot_options.pack(fill="x")

        plot_toolbar = ttk.Frame(self.box_plot_options)
        plot_toolbar.pack(fill="x", padx=8, pady=(8, 4))

        self.btn_plot = tk.Button(plot_toolbar, bg="#c62828", fg="white", relief="raised", command=self.run_analysis)
        self.btn_plot.pack(side="left", padx=(0, 8))
        self.help_plot = add_help_button(plot_toolbar, lambda: tt(self.lang(), "help_plot_now"))
        self.help_plot.pack(side="left", padx=(0, 18))

        self.btn_stats = tk.Button(plot_toolbar, bg="#1565c0", fg="white", relief="raised", command=self.open_stats_window)
        self.btn_stats.pack(side="left", padx=(0, 8))
        self.help_stats = add_help_button(plot_toolbar, lambda: tt(self.lang(), "help_stats_analysis"))
        self.help_stats.pack(side="left")

        p1 = ttk.Frame(self.box_plot_options)
        p1.pack(fill="x", padx=8, pady=(4, 4))

        self.lbl_plot_type = ttk.Label(p1)
        self.lbl_plot_type.pack(side="left")
        self.help_plot_type = add_help_button(p1, lambda: tt(self.lang(), "help_plot_type"))
        self.help_plot_type.pack(side="left", padx=(4, 8))

        self.cmb_plot_type = ttk.Combobox(p1, width=30, state="readonly", textvariable=self.plot_type_display_var)
        self.cmb_plot_type.pack(side="left")
        self.cmb_plot_type.bind("<<ComboboxSelected>>", self._on_plot_type_change)

        self.lbl_mpl_style = ttk.Label(p1)
        self.lbl_mpl_style.pack(side="left", padx=(14, 0))
        self.help_mpl_style = add_help_button(p1, lambda: tt(self.lang(), "help_mpl_style"))
        self.help_mpl_style.pack(side="left", padx=(4, 8))

        self.cmb_mpl_style = ttk.Combobox(
            p1,
            width=22,
            textvariable=self.plot_style_var,
            state="readonly",
            values=["default", "classic", "ggplot", "bmh", "fast", "seaborn-v0_8-whitegrid"],
        )
        self.cmb_mpl_style.pack(side="left")
        self.cmb_mpl_style.bind("<<ComboboxSelected>>", lambda _e: self.update_plot())

        p2 = ttk.Frame(self.box_plot_options)
        p2.pack(fill="x", padx=8, pady=4)

        self.lbl_obs_marker = ttk.Label(p2)
        self.lbl_obs_marker.pack(side="left")
        self.help_obs_marker = add_help_button(p2, lambda: tt(self.lang(), "help_obs_marker"))
        self.help_obs_marker.pack(side="left", padx=(4, 8))

        self.cmb_obs_marker = ttk.Combobox(
            p2,
            width=5,
            textvariable=self.obs_marker_var,
            state="readonly",
            values=["o", "s", "^", "D", ".", "x", "+"],
        )
        self.cmb_obs_marker.pack(side="left")
        self.cmb_obs_marker.bind("<<ComboboxSelected>>", lambda _e: self.update_plot())

        self.lbl_model_line = ttk.Label(p2)
        self.lbl_model_line.pack(side="left", padx=(14, 0))
        self.help_model_line = add_help_button(p2, lambda: tt(self.lang(), "help_model_line"))
        self.help_model_line.pack(side="left", padx=(4, 8))

        self.cmb_model_line = ttk.Combobox(
            p2,
            width=6,
            textvariable=self.model_linestyle_var,
            state="readonly",
            values=["-", "--", "-.", ":"],
        )
        self.cmb_model_line.pack(side="left")
        self.cmb_model_line.bind("<<ComboboxSelected>>", lambda _e: self.update_plot())

        self.lbl_linewidth = ttk.Label(p2)
        self.lbl_linewidth.pack(side="left", padx=(14, 0))
        self.help_linewidth = add_help_button(p2, lambda: tt(self.lang(), "help_linewidth"))
        self.help_linewidth.pack(side="left", padx=(4, 8))

        self.ent_linewidth = ttk.Entry(p2, textvariable=self.linewidth_var, width=6)
        self.ent_linewidth.pack(side="left")

        self.btn_color_obs = ttk.Button(p2, command=self.pick_obs_color)
        self.btn_color_obs.pack(side="left", padx=6)
        self.btn_color_model = ttk.Button(p2, command=self.pick_model_color)
        self.btn_color_model.pack(side="left", padx=6)
        self.btn_color_band = ttk.Button(p2, command=self.pick_band_color)
        self.btn_color_band.pack(side="left", padx=6)

        p3 = ttk.Frame(self.box_plot_options)
        p3.pack(fill="x", padx=8, pady=(4, 8))

        self.chk_points = ttk.Checkbutton(p3, variable=self.show_points_var, command=self.update_plot)
        self.chk_points.pack(side="left", padx=4)
        self.help_points = add_help_button(p3, lambda: tt(self.lang(), "help_show_points"))
        self.help_points.pack(side="left", padx=(0, 10))

        self.chk_model = ttk.Checkbutton(p3, variable=self.show_model_var, command=self.update_plot)
        self.chk_model.pack(side="left", padx=4)
        self.help_model = add_help_button(p3, lambda: tt(self.lang(), "help_show_model"))
        self.help_model.pack(side="left", padx=(0, 10))

        self.chk_band = ttk.Checkbutton(p3, variable=self.show_band_var, command=self.update_plot)
        self.chk_band.pack(side="left", padx=4)
        self.help_band = add_help_button(p3, lambda: tt(self.lang(), "help_show_band"))
        self.help_band.pack(side="left", padx=(0, 10))

        self.chk_grid = ttk.Checkbutton(p3, variable=self.show_grid_var, command=self.update_plot)
        self.chk_grid.pack(side="left", padx=4)
        self.help_grid = add_help_button(p3, lambda: tt(self.lang(), "help_grid"))
        self.help_grid.pack(side="left", padx=(0, 10))

    def _build_main_layout(self):
        self.center = ttk.Frame(self)
        self.center.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.paned = ttk.Panedwindow(self.center, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        self.left_panel = ttk.Frame(self.paned)
        self.right_panel = ttk.Frame(self.paned)

    def _build_data_area(self):
        self.box_data_tables = ttk.LabelFrame(self.left_panel)
        self.box_data_tables.pack(fill="both", expand=True)

        self.lbl_desc_editor = ttk.Label(self.box_data_tables, wraplength=760, justify="left")
        self.lbl_desc_editor.pack(anchor="w", padx=8, pady=(6, 2))

        self.data_notebook = ttk.Notebook(self.box_data_tables)
        self.data_notebook.pack(fill="both", expand=True, padx=6, pady=6)

        self.table_main_frame = ttk.Frame(self.data_notebook)
        self.table_aux_frame = ttk.Frame(self.data_notebook)

        self.table_main = SpreadsheetEditor(self.table_main_frame, self.lang, [tt(self.lang(), "col_failure"), tt(self.lang(), "col_accum_time")], required_count=2)
        self.table_main.pack(fill="both", expand=True)

        self.table_aux = SpreadsheetEditor(self.table_aux_frame, self.lang, [tt(self.lang(), "col_item"), tt(self.lang(), "col_end_obs")], required_count=2)
        self.table_aux.pack(fill="both", expand=True)

        self.data_notebook.add(self.table_main_frame, text=tt(self.lang(), "tab_data"))

    def _build_plot_area(self):
        self.box_plots = ttk.LabelFrame(self.right_panel)
        self.box_plots.pack(fill="both", expand=True)

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=self.box_plots)
        self.canvas_widget = self.canvas_plot.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self.toolbar_plot = NavigationToolbar2Tk(self.canvas_plot, self.box_plots)
        self.toolbar_plot.update()

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value=tt(self.lang(), "status_ready"))
        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

    def _apply_layout(self):
        for pane in self.paned.panes():
            self.paned.forget(pane)

        mode = self.layout_var.get()
        if mode == "table":
            self.paned.add(self.left_panel, weight=1)
        elif mode == "plot":
            self.paned.add(self.right_panel, weight=1)
        else:
            self.paned.add(self.left_panel, weight=1)
            self.paned.add(self.right_panel, weight=2)

    def _apply_language(self):
        lang = self.lang()
        self.title(tt(lang, "app_title"))
        self.menu_bar.entryconfig(0, label=tt(lang, "file_menu"))
        self.menu_bar.entryconfig(1, label=tt(lang, "view_menu"))
        self.menu_bar.entryconfig(2, label=tt(lang, "tools_menu"))
        self.file_menu.entryconfig(0, label=tt(lang, "menu_load_example"))
        self.file_menu.entryconfig(1, label=tt(lang, "menu_export_stats"))
        self.file_menu.entryconfig(3, label=tt(lang, "menu_exit"))
        self.view_menu.entryconfig(0, label=tt(lang, "menu_tables_only"))
        self.view_menu.entryconfig(1, label=tt(lang, "menu_tables_plots"))
        self.view_menu.entryconfig(2, label=tt(lang, "menu_plots_only"))
        self.tools_menu.entryconfig(0, label=tt(lang, "menu_plot_now"))
        self.tools_menu.entryconfig(1, label=tt(lang, "menu_stats_window"))
        self.tools_menu.entryconfig(2, label=tt(lang, "menu_save_plot"))
        self.lbl_language.configure(text=tt(lang, "language"))
        self.box_data_type.configure(text=tt(lang, "data_type"))
        self.box_params.configure(text=tt(lang, "parameters"))
        self.box_plot_options.configure(text=tt(lang, "plot_options"))
        self.box_data_tables.configure(text=tt(lang, "data_tables"))
        self.box_plots.configure(text=tt(lang, "plots"))
        self.lbl_desc_editor.configure(text=tt(lang, "desc_data_editor"))
        self.rb_single.configure(text=tt(lang, "data_type_single"))
        self.rb_same.configure(text=tt(lang, "data_type_same"))
        self.rb_diff.configure(text=tt(lang, "data_type_diff"))
        self.rb_grouped.configure(text=tt(lang, "data_type_grouped"))
        self.lbl_termination.configure(text=tt(lang, "termination_label"))
        self.rb_term_time.configure(text=tt(lang, "term_time"))
        self.rb_term_failure.configure(text=tt(lang, "term_failure"))
        self.lbl_horizon.configure(text=tt(lang, "horizon"))
        self.lbl_k_items.configure(text=tt(lang, "k_items"))
        self.lbl_z_eval.configure(text=tt(lang, "z_eval"))
        self.lbl_bootstrap.configure(text=tt(lang, "bootstrap_reps"))
        self.chk_bootstrap.configure(text=tt(lang, "bootstrap_ci"))
        self.lbl_seed.configure(text=tt(lang, "seed"))
        self.btn_plot.configure(text=tt(lang, "plot_now"))
        self.btn_stats.configure(text=tt(lang, "stats_analysis"))
        self.lbl_plot_type.configure(text=tt(lang, "plot_type"))
        self.lbl_mpl_style.configure(text=tt(lang, "mpl_style"))
        self.lbl_obs_marker.configure(text=tt(lang, "obs_marker"))
        self.lbl_model_line.configure(text=tt(lang, "model_line"))
        self.lbl_linewidth.configure(text=tt(lang, "linewidth"))
        self.btn_color_obs.configure(text=tt(lang, "color_obs"))
        self.btn_color_model.configure(text=tt(lang, "color_model"))
        self.btn_color_band.configure(text=tt(lang, "color_band"))
        self.chk_points.configure(text=tt(lang, "show_points"))
        self.chk_model.configure(text=tt(lang, "show_model"))
        self.chk_band.configure(text=tt(lang, "show_band"))
        self.chk_grid.configure(text=tt(lang, "grid"))
        self.table_main.refresh_language()
        self.table_aux.refresh_language()
        self._update_plot_type_values()
        self._refresh_case_ui()
        self.refresh_stats_window()
        self.update_plot()
        self.status_var.set(tt(lang, "status_ready"))

    def _on_language_change(self, _event=None):
        idx = self.cmb_language.current()
        code = LANG_OPTIONS[idx][0]
        self.lang_var.set(code)
        self._apply_language()


    def _update_plot_type_values(self):
        lang = self.lang()
        self.plot_display_map = {
            "accum": tt(lang, "plot_choice_accum"),
            "accum_loglog": tt(lang, "plot_choice_accum_loglog"),
            "qq": tt(lang, "plot_choice_qq"),
            "ttt": tt(lang, "plot_choice_ttt"),
            "intensity": tt(lang, "plot_choice_intensity"),
        }
        self.plot_reverse_map = {v: k for k, v in self.plot_display_map.items()}
        values = [self.plot_display_map[k] for k in PLOT_IDS]
        self.cmb_plot_type.configure(values=values)
        self.plot_type_display_var.set(self.plot_display_map[self.plot_id])

    def _on_plot_type_change(self, _event=None):
        selected = self.plot_type_display_var.get()
        self.plot_id = self.plot_reverse_map.get(selected, "accum")
        self.update_plot()

    def _toggle_widget(self, widget, enabled: bool):
        widget.configure(state="normal" if enabled else "disabled")

    def _set_notebook_tabs(self, show_aux: bool, main_title: str, aux_title: str):
        for tab in self.data_notebook.tabs():
            self.data_notebook.forget(tab)
        self.data_notebook.add(self.table_main_frame, text=main_title)
        if show_aux:
            self.data_notebook.add(self.table_aux_frame, text=aux_title)

    def _refresh_case_ui(self):
        lang = self.lang()
        case = self.case_var.get()

        if case == "single":
            self.table_main.set_columns(
                [tt(lang, "col_failure"), tt(lang, "col_accum_time")],
                required_count=2,
            )
            self._set_notebook_tabs(False, tt(lang, "tab_failures"), tt(lang, "tab_end_times"))
            self._toggle_widget(self.ent_k_items, False)
            self._toggle_widget(self.ent_horizon, self.term_var.get() == "time")
            self.rb_term_time.configure(state="normal")
            self.rb_term_failure.configure(state="normal")
            self.status_var.set(tt(lang, "status_single"))

        elif case == "same":
            self.term_var.set("time")
            self.table_main.set_columns(
                [tt(lang, "col_item"), tt(lang, "col_failure"), tt(lang, "col_accum_time")],
                required_count=3,
            )
            self._set_notebook_tabs(False, tt(lang, "tab_failures"), tt(lang, "tab_end_times"))
            self._toggle_widget(self.ent_k_items, True)
            self._toggle_widget(self.ent_horizon, True)
            self.rb_term_time.configure(state="disabled")
            self.rb_term_failure.configure(state="disabled")
            self.status_var.set(tt(lang, "status_same"))

        elif case == "diff":
            self.term_var.set("time")
            self.table_main.set_columns(
                [tt(lang, "col_item"), tt(lang, "col_failure"), tt(lang, "col_accum_time")],
                required_count=3,
            )
            self.table_aux.set_columns(
                [tt(lang, "col_item"), tt(lang, "col_end_obs")],
                required_count=2,
            )
            self._set_notebook_tabs(True, tt(lang, "tab_failures"), tt(lang, "tab_end_times"))
            self._toggle_widget(self.ent_k_items, False)
            self._toggle_widget(self.ent_horizon, False)
            self.rb_term_time.configure(state="disabled")
            self.rb_term_failure.configure(state="disabled")
            self.status_var.set(tt(lang, "status_diff"))

        else:
            self.term_var.set("grouped")
            self.table_main.set_columns(
                [tt(lang, "col_interval_start"), tt(lang, "col_interval_end"), tt(lang, "col_failures_interval")],
                required_count=3,
            )
            self._set_notebook_tabs(False, tt(lang, "tab_intervals"), tt(lang, "tab_end_times"))
            self._toggle_widget(self.ent_k_items, False)
            self._toggle_widget(self.ent_horizon, False)
            self.rb_term_time.configure(state="disabled")
            self.rb_term_failure.configure(state="disabled")
            self.status_var.set(tt(lang, "status_grouped"))

        self.update_plot()

    def parse_numeric(self, s: str, field_key: str) -> float:
        try:
            return safe_float(s)
        except Exception:
            raise ValueError(f"{tt(self.lang(), field_key)}")

    def gather_spec(self) -> Dict[str, Any]:
        case = self.case_var.get()
        t_eval = self.parse_numeric(self.t_eval_var.get(), "field_z_eval")

        if case == "single":
            rows = self.table_main.get_all_rows(raw=False)
            times = []
            for row in rows:
                if len(row) < 2 or str(row[1]).strip() == "":
                    continue
                times.append(self.parse_numeric(row[1], "field_accum_time"))

            spec = {
                "case": "single",
                "times": times,
                "termination": self.term_var.get(),
                "t_eval": t_eval,
            }
            if self.term_var.get() == "time":
                spec["t_end"] = self.parse_numeric(self.t_end_var.get(), "field_horizon")
            return spec

        if case == "same":
            rows = self.table_main.get_all_rows(raw=False)
            item_times = []
            for row in rows:
                if len(row) < 3 or str(row[2]).strip() == "":
                    continue
                item = str(row[0]).strip() or "item"
                t = self.parse_numeric(row[2], "field_accum_time")
                item_times.append((item, t))
            return {
                "case": "same",
                "item_times": item_times,
                "k_items": int(float(self.k_var.get())),
                "t_end": self.parse_numeric(self.t_end_var.get(), "field_horizon"),
                "t_eval": t_eval,
            }

        if case == "diff":
            rows = self.table_main.get_all_rows(raw=False)
            item_times = []
            for row in rows:
                if len(row) < 3 or str(row[2]).strip() == "":
                    continue
                item = str(row[0]).strip()
                if not item:
                    raise ValueError(tt(self.lang(), "col_item"))
                t = self.parse_numeric(row[2], "field_accum_time")
                item_times.append((item, t))

            aux = {}
            aux_rows = self.table_aux.get_all_rows(raw=False)
            for row in aux_rows:
                if len(row) < 2 or str(row[1]).strip() == "":
                    continue
                item = str(row[0]).strip()
                if not item:
                    continue
                aux[item] = self.parse_numeric(row[1], "field_end_obs")

            return {
                "case": "diff",
                "item_times": item_times,
                "item_end_times": aux,
                "t_eval": t_eval,
            }

        rows = self.table_main.get_all_rows(raw=False)
        interval_rows = []
        for row in rows:
            if len(row) < 3 or str(row[1]).strip() == "" or str(row[2]).strip() == "":
                continue
            a = self.parse_numeric(row[0], "field_interval_start")
            b = self.parse_numeric(row[1], "field_interval_end")
            n = int(float(str(row[2]).strip().replace(",", ".")))
            interval_rows.append((a, b, n))

        return {
            "case": "grouped",
            "interval_rows": interval_rows,
            "t_eval": t_eval,
        }

    def run_analysis(self):
        lang = self.lang()
        try:
            spec = self.gather_spec()
            self.current_spec = spec

            if spec["case"] == "single":
                result = fit_case_single(
                    spec["times"], spec["termination"], spec.get("t_end"), spec["t_eval"]
                )
            elif spec["case"] == "same":
                result = fit_case_same(
                    spec["item_times"], spec["k_items"], spec["t_end"], spec["t_eval"]
                )
            elif spec["case"] == "diff":
                result = fit_case_diff(
                    spec["item_times"], spec["item_end_times"], spec["t_eval"],
                    messages=["msg_iterative_1c"],
                )
            else:
                result = fit_case_grouped(
                    spec["interval_rows"], spec["t_eval"],
                    messages=["msg_grouped_bootstrap"],
                )

            if self.bootstrap_var.get():
                reps = max(20, int(float(self.bootstrap_reps_var.get())))
                seed_text = self.seed_var.get().strip()
                seed = int(seed_text) if seed_text else None
                bundle = bootstrap_analysis(spec, result, reps=reps, seed=seed)
                result.bootstrap = bundle

                if bundle.reps_ok > 0:
                    result.bootstrap_ci_beta = tuple(np.quantile(bundle.beta_samples, [0.05, 0.95]))
                    result.bootstrap_ci_lambda = tuple(np.quantile(bundle.lambda_samples, [0.05, 0.95]))
                    result.bootstrap_ci_z = tuple(np.quantile(bundle.z_samples, [0.05, 0.95]))
                else:
                    result.messages.append("msg_bootstrap_failed")

            self.current_result = result
            self.status_var.set(tt(lang, "status_done"))
            self.update_plot()
            self.refresh_stats_window()

        except Exception as exc:
            self.status_var.set(tt(lang, "status_error"))
            messagebox.showerror(tt(lang, "error_title"), str(exc))
