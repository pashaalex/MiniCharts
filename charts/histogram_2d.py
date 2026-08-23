import seaborn as sns

from .base import ChartType


class Histogram2DChart(ChartType):
    display_name = "2D Histogram"

    def build_settings_ui(self, parent, dataframe):
        columns = self._begin_settings(parent, dataframe)
        self.x_column = self._add_column_setting("X column:", columns)
        self.y_column = self._add_column_setting("Y column:", columns, 1)
        self.bins = self._add_text_setting("Bins:", "30")
        self._finish_settings()

    def draw_chart(self, dataframe):
        sns.histplot(
            data=dataframe,
            x=self.x_column.get(),
            y=self.y_column.get(),
            bins=int(self.bins.get()),
            cbar=True,
        )
