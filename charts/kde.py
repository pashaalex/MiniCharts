import seaborn as sns

from .base import TrimmedValueChart


class KdeChart(TrimmedValueChart):
    display_name = "KDE plot"

    def draw_chart(self, dataframe):
        sns.kdeplot(
            data=dataframe,
            x=self.value_column.get(),
            hue=self.group_column.get() or None,
        )
