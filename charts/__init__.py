import seaborn as sns

from .bar import BarChart
from .base import ChartType, TrimmedValueChart, trim_values
from .box_plot import BoxPlotChart
from .heatmap import HeatmapChart
from .histogram import HistogramChart
from .histogram_2d import Histogram2DChart
from .kde import KdeChart
from .kde_2d import Kde2DChart
from .registry import get_registered_charts, register_chart
from .scatter import ScatterChart
from .violin_plot import ViolinPlotChart


sns.set_theme(style="whitegrid")

for chart in (
    ScatterChart,
    HistogramChart,
    BarChart,
    BoxPlotChart,
    ViolinPlotChart,
    KdeChart,
    HeatmapChart,
    Histogram2DChart,
    Kde2DChart,
):
    register_chart(chart)


__all__ = [
    "BarChart",
    "BoxPlotChart",
    "ChartType",
    "HeatmapChart",
    "Histogram2DChart",
    "HistogramChart",
    "Kde2DChart",
    "KdeChart",
    "ScatterChart",
    "TrimmedValueChart",
    "ViolinPlotChart",
    "get_registered_charts",
    "register_chart",
    "trim_values",
]
