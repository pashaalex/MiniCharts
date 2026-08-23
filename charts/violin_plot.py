import seaborn as sns

from .base import TrimmedValueChart


class ViolinPlotChart(TrimmedValueChart):
    display_name = "Violin plot"

    def draw_chart(self, dataframe):
        sns.violinplot(
            data=dataframe,
            x=self.group_column.get() or None,
            y=self.value_column.get(),
            inner="quart",
        )
