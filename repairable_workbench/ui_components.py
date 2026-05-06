from __future__ import annotations

import csv
from typing import Any, List, Optional, Sequence

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from .i18n import tt


class ToolTip:
    def __init__(self, widget: tk.Widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tip_window: Optional[tk.Toplevel] = None
        self.label: Optional[tk.Label] = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        text = self.text_func()
        if not text or self.tip_window is not None:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.geometry(f"+{x}+{y}")
        self.label = tk.Label(self.tip_window, text=text, bg="#fff8dc", fg="black", relief="solid", bd=1, padx=6, pady=4, justify="left", wraplength=320)
        self.label.pack()

    def hide(self, _event=None):
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None
            self.label = None


def add_help_button(parent, text_func):
    btn = tk.Label(parent, text="?", bg="#f2f2f2", fg="#333333", relief="solid", bd=1, width=2, cursor="question_arrow", font=("Segoe UI", 8, "bold"))
    ToolTip(btn, text_func)
    return btn


class SpreadsheetEditor(ttk.Frame):
    def __init__(self, master, get_lang, columns: Sequence[str], required_count: Optional[int] = None, min_blank_rows: int = 220, grow_chunk: int = 120, protected_prefix_key: str = "extra_prefix"):
        super().__init__(master)
        self.get_lang = get_lang
        self.required_count = required_count if required_count is not None else len(columns)
        self.columns = list(columns)
        self.min_blank_rows = min_blank_rows
        self.grow_chunk = grow_chunk
        self.protected_prefix_key = protected_prefix_key
        self.data: List[List[str]] = []
        self.vars: List[List[tk.StringVar]] = []
        self.entries: List[List[tk.Entry]] = []
        self.header_labels: List[tk.Label] = []
        self.focus_row = 0
        self.focus_col = 0
        self._build_toolbar()
        self._build_sheet_container()
        self.set_columns(columns, self.required_count)

    def lang(self) -> str:
        return self.get_lang()

    def _build_toolbar(self):
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(fill="x", pady=(0, 4))
        self.btn_add_col = ttk.Button(self.toolbar, command=self.add_column)
        self.btn_add_col.pack(side="left", padx=2)
        self.btn_remove_col = ttk.Button(self.toolbar, command=self.remove_column)
        self.btn_remove_col.pack(side="left", padx=2)
        self.btn_paste = ttk.Button(self.toolbar, command=self.paste_from_clipboard)
        self.btn_paste.pack(side="left", padx=2)
        self.btn_clear = ttk.Button(self.toolbar, command=self.clear_user_data)
        self.btn_clear.pack(side="left", padx=2)
        self.btn_import = ttk.Button(self.toolbar, command=self.import_csv)
        self.btn_import.pack(side="left", padx=2)
        self.btn_export = ttk.Button(self.toolbar, command=self.export_csv)
        self.btn_export.pack(side="left", padx=2)
        self.refresh_language()

    def _build_sheet_container(self):
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(outer, bg="white", highlightthickness=1, highlightbackground="#a0a0a0")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.vscroll.pack(side="right", fill="y")
        self.hscroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.hscroll.pack(fill="x")
        self.canvas.configure(yscrollcommand=self.vscroll.set, xscrollcommand=self.hscroll.set)
        self.inner = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        for widget in (self.canvas, self.inner):
            widget.bind("<MouseWheel>", self._scroll_windows)
            widget.bind("<Button-4>", self._scroll_linux)
            widget.bind("<Button-5>", self._scroll_linux)
            widget.bind("<Shift-MouseWheel>", self._shift_scroll_windows)

    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=max(event.width, self.inner.winfo_reqwidth()))

    def _scroll_windows(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _shift_scroll_windows(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _scroll_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        return "break"

    def refresh_language(self):
        self.btn_add_col.configure(text=tt(self.lang(), "toolbar_add_col"))
        self.btn_remove_col.configure(text=tt(self.lang(), "toolbar_remove_col"))
        self.btn_paste.configure(text=tt(self.lang(), "toolbar_paste"))
        self.btn_clear.configure(text=tt(self.lang(), "toolbar_clear"))
        self.btn_import.configure(text=tt(self.lang(), "toolbar_import"))
        self.btn_export.configure(text=tt(self.lang(), "toolbar_export"))

    def _rebuild_grid(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
        self.header_labels = []
        self.entries = []
        self.vars = []
        for c, name in enumerate(self.columns):
            lbl = tk.Label(self.inner, text=name, bg="#e9e9e9", fg="black", relief="solid", bd=1, font=("Segoe UI", 10, "bold"), padx=4, pady=4)
            lbl.grid(row=0, column=c, sticky="nsew", padx=0, pady=0)
            self.inner.grid_columnconfigure(c, weight=1, minsize=150)
            self.header_labels.append(lbl)
        for r in range(len(self.data)):
            row_vars = []
            row_entries = []
            for c in range(len(self.columns)):
                var = tk.StringVar(value=self.data[r][c] if c < len(self.data[r]) else "")
                ent = tk.Entry(self.inner, textvariable=var, relief="solid", bd=1, bg="white", fg="black", insertbackground="black", highlightthickness=0, justify="center")
                ent.grid(row=r + 1, column=c, sticky="nsew", padx=0, pady=0, ipady=4)
                ent.bind("<FocusIn>", lambda e, rr=r, cc=c: self._on_focus_cell(rr, cc))
                ent.bind("<Button-1>", lambda e, rr=r, cc=c: self._on_focus_cell(rr, cc))
                ent.bind("<KeyRelease>", lambda e, rr=r, cc=c: self._on_cell_edited(rr, cc))
                ent.bind("<Tab>", lambda e, rr=r, cc=c: self._move_next_cell(e, rr, cc))
                ent.bind("<Return>", lambda e, rr=r, cc=c: self._move_next_cell(e, rr, cc))
                ent.bind("<MouseWheel>", self._scroll_windows)
                ent.bind("<Button-4>", self._scroll_linux)
                ent.bind("<Button-5>", self._scroll_linux)
                ent.bind("<Shift-MouseWheel>", self._shift_scroll_windows)
                row_vars.append(var)
                row_entries.append(ent)
            self.vars.append(row_vars)
            self.entries.append(row_entries)
        self._sync_vars_to_data()
        self._on_inner_configure()

    def _sync_vars_to_data(self):
        for r in range(len(self.vars)):
            for c in range(len(self.vars[r])):
                self.data[r][c] = self.vars[r][c].get()

    def _on_focus_cell(self, row: int, col: int):
        self.focus_row = row
        self.focus_col = col

    def _on_cell_edited(self, row: int, col: int):
        try:
            self.data[row][col] = self.vars[row][col].get()
        except Exception:
            pass
        self.ensure_blank_rows()

    def _move_next_cell(self, event, row: int, col: int):
        self._sync_vars_to_data()
        self.ensure_blank_rows()
        if col < len(self.columns) - 1:
            next_row, next_col = row, col + 1
        else:
            next_row, next_col = row + 1, 0
        if next_row >= len(self.entries):
            self.ensure_blank_rows()
            self._rebuild_grid()
        try:
            target = self.entries[next_row][next_col]
            target.focus_set()
            target.icursor("end")
        except Exception:
            pass
        return "break"

    def set_columns(self, columns: Sequence[str], required_count: Optional[int] = None):
        if required_count is not None:
            self.required_count = required_count
        old_rows = self.get_all_rows(raw=True)
        self.columns = list(columns)
        new_data = []
        for row in old_rows:
            vals = list(row)
            if len(vals) < len(self.columns):
                vals = vals + [""] * (len(self.columns) - len(vals))
            else:
                vals = vals[:len(self.columns)]
            new_data.append(vals)
        self.data = new_data
        self.ensure_blank_rows()
        self._rebuild_grid()

    def add_column(self):
        name = simpledialog.askstring(tt(self.lang(), "new_col_title"), tt(self.lang(), "new_col_prompt"), parent=self)
        if name is None:
            return
        name = name.strip()
        if not name:
            name = f"{tt(self.lang(), self.protected_prefix_key)} {len(self.columns) - self.required_count + 1}"
        if name in self.columns:
            base = name
            idx = 2
            while name in self.columns:
                name = f"{base} {idx}"
                idx += 1
        self.set_columns(self.columns + [name], self.required_count)

    def remove_column(self):
        if len(self.columns) <= self.required_count:
            messagebox.showinfo(tt(self.lang(), "columns_title"), tt(self.lang(), "mandatory_columns_msg"))
            return
        self.set_columns(self.columns[:-1], self.required_count)

    def ensure_blank_rows(self):
        while len(self.data) < self.min_blank_rows:
            self.data.append(["" for _ in self.columns])
        last_nonblank_index = -1
        for idx, row in enumerate(self.data):
            if any(str(v).strip() != "" for v in row):
                last_nonblank_index = idx
        if len(self.data) - last_nonblank_index < 25:
            for _ in range(self.grow_chunk):
                self.data.append(["" for _ in self.columns])
        for i in range(len(self.data)):
            if len(self.data[i]) < len(self.columns):
                self.data[i].extend([""] * (len(self.columns) - len(self.data[i])))
            elif len(self.data[i]) > len(self.columns):
                self.data[i] = self.data[i][:len(self.columns)]

    def clear_user_data(self):
        self.data = [["" for _ in self.columns] for _ in range(self.min_blank_rows)]
        self._rebuild_grid()

    def get_all_rows(self, raw: bool = False) -> List[List[str]]:
        if self.vars:
            self._sync_vars_to_data()
        rows = [[str(v) for v in row] for row in self.data]
        if raw:
            return rows
        usable = []
        for row in rows:
            if any(str(v).strip() != "" for v in row):
                usable.append(row)
        return usable

    def set_rows(self, rows: Sequence[Sequence[Any]]):
        self.data = []
        for row in rows:
            vals = list(row)
            if len(vals) < len(self.columns):
                vals = vals + [""] * (len(self.columns) - len(vals))
            else:
                vals = vals[:len(self.columns)]
            self.data.append([str(v) for v in vals])
        self.ensure_blank_rows()
        self._rebuild_grid()

    def paste_from_clipboard(self):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            messagebox.showwarning(tt(self.lang(), "clipboard_title"), tt(self.lang(), "clipboard_empty"))
            return
        lines = [line for line in text.splitlines() if line.strip() != ""]
        if not lines:
            return
        data = [line.split("	") for line in lines]
        start_row = self.focus_row
        start_col = self.focus_col
        needed_rows = start_row + len(data)
        while len(self.data) < needed_rows + 5:
            self.data.append(["" for _ in self.columns])
        if self.vars:
            self._sync_vars_to_data()
        for r_off, row in enumerate(data):
            target_row = start_row + r_off
            while len(self.data[target_row]) < len(self.columns):
                self.data[target_row].append("")
            for c_off, value in enumerate(row):
                target_col = start_col + c_off
                if target_col >= len(self.columns):
                    break
                self.data[target_row][target_col] = value
        self.ensure_blank_rows()
        self._rebuild_grid()

    def import_csv(self):
        path = filedialog.askopenfilename(title=tt(self.lang(), "import_csv_title"), filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not path:
            return
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
        if not data:
            return
        if len(data[0]) == len(self.columns):
            header_candidate = [c.strip() for c in data[0]]
            if header_candidate == [c.strip() for c in self.columns]:
                data = data[1:]
        self.set_rows(data)

    def export_csv(self):
        path = filedialog.asksaveasfilename(title=tt(self.lang(), "export_csv_title"), defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        rows = self.get_all_rows(raw=False)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(rows)
