import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List

import pandas as pd

from csv_importer import (
    ColumnSettings,
    CsvSettings,
    ImportSettings,
    apply_column_settings,
    import_csv,
    pandas_dtype_to_data_type,
)
from report_builder import ReportBuilderWindow


ENCODINGS = {
    "UTF-8": "utf-8",
    "UTF-8 with BOM": "utf-8-sig",
    "Windows-1251": "cp1251",
    "Windows-1252": "cp1252",
    "Latin-1": "latin-1",
    "ASCII": "ascii",
}
SEPARATORS = {"Comma (,)": ",", "Semicolon (;)": ";", "Tab": "\t"}
DECIMAL_SEPARATORS = {"Dot (.)": ".", "Comma (,)": ","}
DATA_TYPES = ("string", "integer", "float", "boolean", "datetime")
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class ImportWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.title("Import CSV")
        self.geometry("900x700")

        self.filename = tk.StringVar()
        self.encoding = tk.StringVar(value="UTF-8")
        self.separator = tk.StringVar(value="Comma (,)")
        self.decimal_separator = tk.StringVar(value="Dot (.)")
        self.column_controls: List[Dict[str, object]] = []
        self.preview_source = pd.DataFrame()
        self.generate_column_names = False

        self._build_file_settings()
        self._build_columns_area()
        self._build_preview_area()
        self._build_buttons()

    def _build_file_settings(self) -> None:
        frame = ttk.LabelFrame(self, text="CSV settings", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="File:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.filename).grid(
            row=0, column=1, columnspan=4, sticky="ew", padx=5
        )
        ttk.Button(frame, text="Browse...", command=self._choose_file).grid(row=0, column=5)

        ttk.Label(frame, text="Encoding:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        encoding_box = ttk.Combobox(
            frame, textvariable=self.encoding, values=list(ENCODINGS), state="readonly", width=14
        )
        encoding_box.grid(row=1, column=1, sticky="w", padx=5, pady=(10, 0))

        ttk.Label(frame, text="Separator:").grid(row=1, column=2, sticky="w", pady=(10, 0))
        separator_box = ttk.Combobox(
            frame, textvariable=self.separator, values=list(SEPARATORS), state="readonly", width=16
        )
        separator_box.grid(row=1, column=3, sticky="w", padx=5, pady=(10, 0))

        ttk.Label(frame, text="Decimal:").grid(row=1, column=4, sticky="w", pady=(10, 0))
        decimal_box = ttk.Combobox(
            frame,
            textvariable=self.decimal_separator,
            values=list(DECIMAL_SEPARATORS),
            state="readonly",
            width=12,
        )
        decimal_box.grid(row=1, column=5, sticky="w", pady=(10, 0))

        for box in (encoding_box, separator_box, decimal_box):
            box.bind("<<ComboboxSelected>>", self._csv_option_changed)

        frame.columnconfigure(1, weight=1)

    def _build_columns_area(self) -> None:
        outer = ttk.LabelFrame(self, text="Columns", padding=5)
        outer.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.columns_frame = ttk.Frame(self.canvas)

        self.columns_frame.bind(
            "<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.columns_frame, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(
            self.columns_frame,
            text="Choose a CSV file.",
        ).pack(pady=30)

    def _build_preview_area(self) -> None:
        outer = ttk.LabelFrame(self, text="Preview Data", padding=5)
        outer.pack(fill="x", padx=10, pady=(10, 0))

        self.preview_table = ttk.Treeview(outer, show="headings", height=6)
        vertical = ttk.Scrollbar(outer, orient="vertical", command=self.preview_table.yview)
        horizontal = ttk.Scrollbar(outer, orient="horizontal", command=self.preview_table.xview)
        self.preview_table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )

        self.preview_table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        outer.columnconfigure(0, weight=1)

        self.preview_status = ttk.Label(outer, text="No data loaded")
        self.preview_status.grid(row=2, column=0, sticky="w", pady=(3, 0))

    def _build_buttons(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="x")
        ttk.Button(frame, text="Read structure", command=self._read_structure_with_header).pack(
            side="left"
        )
        ttk.Button(
            frame,
            text="Generate column names",
            command=self._read_structure_with_generated_names,
        ).pack(side="left", padx=8)
        ttk.Button(frame, text="Import Data", command=self._import).pack(side="right")

    def _choose_file(self) -> None:
        filename = filedialog.askopenfilename(
            parent=self,
            title="Choose CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if filename:
            self.filename.set(filename)
            self.generate_column_names = False
            self._read_structure()

    def _csv_option_changed(self, event: tk.Event) -> None:
        if self.filename.get():
            self._read_structure(redetect_data_types=True)

    def _csv_settings(self) -> CsvSettings:
        return CsvSettings(
            encoding=ENCODINGS[self.encoding.get()],
            separator=SEPARATORS[self.separator.get()],
            decimal_separator=DECIMAL_SEPARATORS[self.decimal_separator.get()],
            first_row_has_header=not self.generate_column_names,
        )

    def _read_structure_with_header(self) -> None:
        self.generate_column_names = False
        self._read_structure()

    def _read_structure_with_generated_names(self) -> None:
        self.generate_column_names = True
        self._read_structure()

    def _read_structure(self, redetect_data_types: bool = False) -> None:
        try:
            csv_settings = self._csv_settings()
            self.preview_source = pd.read_csv(
                self.filename.get(),
                encoding=csv_settings.encoding,
                sep=csv_settings.separator,
                decimal=csv_settings.decimal_separator,
                nrows=10,
                header=0 if csv_settings.first_row_has_header else None,
            )
            if self.generate_column_names:
                self.preview_source.columns = [
                    f"Column{index + 1}" for index in range(len(self.preview_source.columns))
                ]
            self._show_column_controls(
                list(self.preview_source.columns),
                redetect_data_types=redetect_data_types,
            )
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)

    def _show_column_controls(
        self, columns: List[str], redetect_data_types: bool = False
    ) -> None:
        previous_settings = {
            control["source_name"]: {
                "include": control["include"].get(),
                "result_name": control["result_name"].get(),
                "data_type": control["data_type"].get(),
                "datetime_format": control["datetime_format"].get(),
            }
            for control in self.column_controls
        }

        for widget in self.columns_frame.winfo_children():
            widget.destroy()
        self.column_controls.clear()

        headers = ("Import", "Source name", "Result name", "Data type", "Datetime format")
        for index, header in enumerate(headers):
            ttk.Label(self.columns_frame, text=header).grid(
                row=0, column=index, sticky="w", padx=5, pady=5
            )

        for row, source_name in enumerate(columns, start=1):
            previous = previous_settings.get(source_name, {})
            include = tk.BooleanVar(value=previous.get("include", True))
            result_name = tk.StringVar(value=previous.get("result_name", source_name))
            detected_data_type = pandas_dtype_to_data_type(
                self.preview_source[source_name].dtype
            )
            data_type = tk.StringVar(
                value=(
                    detected_data_type
                    if redetect_data_types
                    else previous.get("data_type", detected_data_type)
                )
            )
            datetime_format = tk.StringVar(value=previous.get("datetime_format", ""))

            ttk.Checkbutton(
                self.columns_frame, variable=include, command=self._refresh_preview
            ).grid(row=row, column=0, padx=5)
            ttk.Label(self.columns_frame, text=source_name).grid(
                row=row, column=1, sticky="w", padx=5, pady=3
            )
            ttk.Entry(self.columns_frame, textvariable=result_name).grid(
                row=row, column=2, sticky="ew", padx=5, pady=3
            )
            type_box = ttk.Combobox(
                self.columns_frame,
                textvariable=data_type,
                values=DATA_TYPES,
                state="readonly",
                width=12,
            )
            type_box.grid(row=row, column=3, padx=5, pady=3)
            format_entry = ttk.Entry(
                self.columns_frame,
                textvariable=datetime_format,
                state="normal" if data_type.get() == "datetime" else "disabled",
            )
            format_entry.grid(row=row, column=4, sticky="ew", padx=5, pady=3)
            type_box.bind(
                "<<ComboboxSelected>>",
                lambda event,
                variable=data_type,
                entry=format_entry,
                format_variable=datetime_format: self._data_type_changed(
                    variable, entry, format_variable
                ),
            )

            self.column_controls.append(
                {
                    "source_name": source_name,
                    "include": include,
                    "result_name": result_name,
                    "data_type": data_type,
                    "datetime_format": datetime_format,
                }
            )
            result_name.trace_add("write", self._preview_variable_changed)
            data_type.trace_add("write", self._preview_variable_changed)
            datetime_format.trace_add("write", self._preview_variable_changed)

        self.columns_frame.columnconfigure(2, weight=1)
        self.columns_frame.columnconfigure(4, weight=1)
        self._refresh_preview()

    def _data_type_changed(
        self,
        data_type: tk.StringVar,
        format_entry: ttk.Entry,
        datetime_format: tk.StringVar,
    ) -> None:
        is_datetime = data_type.get() == "datetime"
        format_entry.configure(state="normal" if is_datetime else "disabled")
        if is_datetime and not datetime_format.get():
            datetime_format.set(DEFAULT_DATETIME_FORMAT)

    def _preview_variable_changed(self, *args: object) -> None:
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        if not self.column_controls:
            return

        for item in self.preview_table.get_children():
            self.preview_table.delete(item)

        try:
            preview = apply_column_settings(
                self.preview_source,
                self._import_settings().columns,
            )
            column_ids = [f"column_{index}" for index in range(len(preview.columns))]
            self.preview_table.configure(columns=column_ids)

            for column_id, name in zip(column_ids, preview.columns):
                self.preview_table.heading(column_id, text=str(name))
                self.preview_table.column(column_id, width=140, minwidth=80)

            for row in preview.itertuples(index=False, name=None):
                self.preview_table.insert("", "end", values=[str(value) for value in row])

            self.preview_status.configure(text=f"Preview: {len(preview)} row(s)")
        except Exception as error:
            self.preview_table.configure(columns=())
            self.preview_status.configure(text=f"Preview error: {error}")

    def _import_settings(self) -> ImportSettings:
        columns = [
            ColumnSettings(
                source_name=control["source_name"],
                import_column=control["include"].get(),
                result_name=control["result_name"].get(),
                data_type=control["data_type"].get(),
                datetime_format=control["datetime_format"].get(),
            )
            for control in self.column_controls
        ]
        return ImportSettings(csv=self._csv_settings(), columns=columns)

    def _import(self) -> None:
        if not self.column_controls:
            messagebox.showinfo("Import CSV", "Read the file structure first.", parent=self)
            return

        try:
            dataframe = import_csv(self.filename.get(), self._import_settings())
            ReportBuilderWindow(self.master, dataframe)
            self.destroy()
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    import_window = ImportWindow(root)
    import_window.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()


if __name__ == "__main__":
    main()
