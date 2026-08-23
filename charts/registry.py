from typing import List, Type

from .base import ChartType


CHART_TYPES: List[Type[ChartType]] = []


def register_chart(chart_type: Type[ChartType]) -> None:
    CHART_TYPES.append(chart_type)


def get_registered_charts() -> List[Type[ChartType]]:
    return CHART_TYPES
