import seaborn as sns

from .base import ChartType


class Kde2DChart(ChartType):
    display_name = "2D KDE"

    def build_settings_ui(self, parent, dataframe):
        columns = self._begin_settings(parent, dataframe)
        self.x_column = self._add_column_setting("X column:", columns)
        self.y_column = self._add_column_setting("Y column:", columns, 1)
        self.group_column = self._add_column_setting(
            "Group column:", columns, optional=True
        )
        self.levels = self._add_text_setting("Levels:", "8")
        self.filled = self._add_boolean_setting("Filled:")
        self._finish_settings()

    def draw_chart(self, dataframe):
        sns.kdeplot(
            data=dataframe,
            x=self.x_column.get(),
            y=self.y_column.get(),
            hue=self.group_column.get() or None,
            levels=int(self.levels.get()),
            fill=self.filled.get(),
        )
