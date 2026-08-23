import seaborn as sns

from .base import TrimmedValueChart


class HistogramChart(TrimmedValueChart):
    display_name = "Histogram"

    def _build_specific_settings(self):
        self.group_display = self._add_choice_setting(
            "Group display:", ("Layer", "Dodge"), "Layer"
        )
        self.bins = self._add_text_setting("Bins:", "10")

    def draw_chart(self, dataframe):
        group = self.group_column.get()
        multiple = "layer" if self.group_display.get() == "Layer" else "dodge"
        sns.histplot(
            data=dataframe,
            x=self.value_column.get(),
            hue=group or None,
            bins=int(self.bins.get()),
            multiple=multiple if group else "layer",
            kde=False,
        )
