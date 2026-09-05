import tkinter as tk
from tkinter import ttk

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import pandas as pd


def trim_values(
    dataframe: pd.DataFrame,
    value_column: str,
    group_column: str,
    lower_percent: float,
    upper_percent: float,
) -> pd.DataFrame:
    if lower_percent == 0 and upper_percent == 0:
        return dataframe

    def trim_group(group: pd.DataFrame) -> pd.DataFrame:
        series = group[value_column]
        lower = series.quantile(lower_percent / 100)
        upper = series.quantile(1 - upper_percent / 100)
        return group[series.between(lower, upper)]

    if group_column:
        return pd.concat(
            trim_group(group)
            for _, group in dataframe.groupby(group_column, dropna=False)
        )
    return trim_group(dataframe)


class ChartType:
    display_name = "Chart"

    def _begin_settings(self, parent, dataframe):
        self._parent = parent
        self._row = 0
        self.title = tk.StringVar(master=parent, value=self.display_name)
        return list(dataframe.columns)

    def _add_setting(self, label, widget):
        ttk.Label(self._parent, text=label).grid(
            row=self._row, column=0, sticky="w", padx=5, pady=5
        )
        widget.grid(
            row=self._row,
            column=1,
            sticky="w" if isinstance(widget, ttk.Checkbutton) else "ew",
            padx=5,
            pady=5,
        )
        self._row += 1

    @staticmethod
    def _column_at(columns, index):
        if not columns:
            return ""
        return columns[index] if index < len(columns) else columns[0]

    def _add_column_setting(self, label, columns, default_index=0, optional=False):
        default = "" if optional else self._column_at(columns, default_index)
        variable = tk.StringVar(master=self._parent, value=default)
        self._add_setting(
            label,
            ttk.Combobox(
                self._parent,
                textvariable=variable,
                values=([""] + columns) if optional else columns,
                state="readonly",
            ),
        )
        return variable

    def _add_text_setting(self, label, default):
        variable = tk.StringVar(master=self._parent, value=default)
        self._add_setting(label, ttk.Entry(self._parent, textvariable=variable))
        return variable

    def _add_choice_setting(self, label, values, default):
        variable = tk.StringVar(master=self._parent, value=default)
        self._add_setting(
            label,
            ttk.Combobox(
                self._parent, textvariable=variable, values=values, state="readonly"
            ),
        )
        return variable

    def _add_boolean_setting(self, label, default=False):
        variable = tk.BooleanVar(master=self._parent, value=default)
        self._add_setting(label, ttk.Checkbutton(self._parent, variable=variable))
        return variable

    def _finish_settings(self):
        self._add_setting("Title:", ttk.Entry(self._parent, textvariable=self.title))
        self._parent.columnconfigure(1, weight=1)

    def build_settings_ui(self, parent: ttk.Frame, dataframe: pd.DataFrame) -> None:
        raise NotImplementedError

    def prepare_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe

    def draw_chart(self, dataframe: pd.DataFrame) -> None:
        raise NotImplementedError

    def build_chart(self, dataframe: pd.DataFrame) -> None:
        dataframe = self.prepare_dataframe(dataframe)
        plt.figure()
        self.draw_chart(dataframe)
        plt.title(self.title.get())
        plt.tight_layout()
        plt.show()


class TrimmedValueChart(ChartType):
    def build_settings_ui(self, parent: ttk.Frame, dataframe: pd.DataFrame) -> None:
        columns = self._begin_settings(parent, dataframe)
        self.value_column = self._add_column_setting("Value column:", columns)
        self.group_column = self._add_column_setting(
            "Group column:", columns, optional=True
        )
        self._build_specific_settings()
        self.trim_lower = self._add_text_setting("Trim lower, %:", "0")
        self.trim_upper = self._add_text_setting("Trim upper, %:", "0")
        self._finish_settings()

    def _build_specific_settings(self):
        pass

    def prepare_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return trim_values(
            dataframe,
            self.value_column.get(),
            self.group_column.get(),
            float(self.trim_lower.get()),
            float(self.trim_upper.get()),
        )
