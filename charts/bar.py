import matplotlib.pyplot as plt

from .base import ChartType


class BarChart(ChartType):
    display_name = "Bar chart"

    def build_settings_ui(self, parent, dataframe):
        columns = self._begin_settings(parent, dataframe)
        self.x_column = self._add_column_setting("X column:", columns)
        self.value_column = self._add_column_setting("Value column:", columns, 1)
        self.group_column = self._add_column_setting(
            "Group column:", columns, optional=True
        )
        self.aggregation = self._add_choice_setting(
            "Aggregation:", ("sum", "mean", "count"), "sum"
        )
        self._finish_settings()

    def build_chart(self, dataframe):
        x, value = self.x_column.get(), self.value_column.get()
        group, aggregation = self.group_column.get(), self.aggregation.get()
        if group:
            values = dataframe.groupby([x, group])[value].agg(aggregation).unstack(group)
        else:
            values = dataframe.groupby(x)[value].agg(aggregation)
        axes = values.plot(kind="bar")
        axes.set_title(self.title.get())
        plt.tight_layout()
        plt.show()
