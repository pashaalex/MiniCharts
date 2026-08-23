import seaborn as sns

from .base import ChartType


class HeatmapChart(ChartType):
    display_name = "Heatmap"

    def build_settings_ui(self, parent, dataframe):
        columns = self._begin_settings(parent, dataframe)
        self.x_column = self._add_column_setting("X column:", columns)
        self.y_column = self._add_column_setting("Y column:", columns, 1)
        self.value_column = self._add_column_setting("Value column:", columns, 2)
        self.aggregation = self._add_choice_setting(
            "Aggregation:", ("sum", "mean", "count"), "sum"
        )
        self._finish_settings()

    def draw_chart(self, dataframe):
        values = dataframe.pivot_table(
            index=self.y_column.get(),
            columns=self.x_column.get(),
            values=self.value_column.get(),
            aggfunc=self.aggregation.get(),
        )
        sns.heatmap(values, annot=True)
