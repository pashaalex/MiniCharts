import seaborn as sns

from .base import TrimmedValueChart


class BoxPlotChart(TrimmedValueChart):
    display_name = "Box plot"

    def draw_chart(self, dataframe):
        sns.boxplot(
            data=dataframe,
            x=self.group_column.get() or None,
            y=self.value_column.get(),
        )
