import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

import pandas as pd

from charts import ChartType, get_registered_charts


class ReportBuilderWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc, dataframe: pd.DataFrame) -> None:
        super().__init__(parent)
        self.title("Report Builder")
        self.geometry("550x400")
        self.dataframe = dataframe
        self.current_chart: Optional[ChartType] = None

        chart_types = get_registered_charts()
        self.chart_classes = {chart_type.display_name: chart_type for chart_type in chart_types}
        self.chart_name = tk.StringVar(value=chart_types[0].display_name)

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Chart type:").pack(side="left")
        chart_box = ttk.Combobox(
            top,
            textvariable=self.chart_name,
            values=list(self.chart_classes),
            state="readonly",
        )
        chart_box.pack(side="left", fill="x", expand=True, padx=(8, 0))
        chart_box.bind("<<ComboboxSelected>>", self._chart_type_changed)

        self.settings_frame = ttk.LabelFrame(self, text="Chart settings", padding=10)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ttk.Button(self, text="Build Chart", command=self._build_chart).pack(pady=(0, 10))

        self.protocol("WM_DELETE_WINDOW", parent.destroy)
        self._show_chart_settings()

    def _chart_type_changed(self, event: tk.Event) -> None:
        self._show_chart_settings()

    def _show_chart_settings(self) -> None:
        for widget in self.settings_frame.winfo_children():
            widget.destroy()

        chart_class = self.chart_classes[self.chart_name.get()]
        self.current_chart = chart_class()
        self.current_chart.build_settings_ui(self.settings_frame, self.dataframe)

    def _build_chart(self) -> None:
        try:
            self.current_chart.build_chart(self.dataframe)
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)
