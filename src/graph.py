import altair as alt
import pandas as pd

from translation import Translate
from data import Data
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=60)


@cached(cache)
class Graph:
    data = None
    t = None

    def __init__(self, data: Data, t: Translate):
        self.data = data
        self.t = t

    def formatter(self, name: str, suffix: str = "") -> str:
        if suffix == "":
            return self.t.get(f"{name}")
        return " - ".join([
                self.t.get(f"{name}"),
                self.t.get(f"suffix_{suffix}")
            ])

    def render_global_chart(
        self,
        data: pd.DataFrame,
        feature: str,
        suffix: str,
        scale: alt.Scale,
        title: str,
        padding: int = 5,
        width: int = 700,
        height: int = 500,
    ):
        y_axis = feature if suffix == "" else f"{feature}_{suffix}"
        return (
            alt.Chart(data)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title=title),
                y=alt.Y(f"{y_axis}:Q",
                        title=self.formatter(feature, suffix), scale=scale),
                tooltip=[
                    alt.Tooltip(f"{y_axis}", title=self.formatter(
                        feature, suffix)),
                    alt.Tooltip("date", title=self.t.str_date, type="temporal")
                ]
            )
            .configure_scale(continuousPadding=padding)
            .properties(width=width, height=height)
            .interactive()
        )

    def render_regional_chart(
        self,
        data: pd.DataFrame,
        feature: str,
        suffix: str,
        scale: alt.Scale,
        title: str,
        alt_title: str,
        padding: int = 5,
        width: int = 700,
        height: int = 500,
        legend_position: str = "top-left",
    ):
        y_axis = feature if suffix == "" else f"{feature}_{suffix}"
        return (
            alt.Chart(data)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title=title),
                y=alt.Y(f"{y_axis}:Q", title=self.formatter(feature, suffix),
                        scale=scale),
                color=alt.Color("region_name:N", title=alt_title),
                tooltip=[
                    alt.Tooltip("region_name", title=alt_title),
                    alt.Tooltip(f"{y_axis}", title=self.formatter(
                        feature, suffix)),
                    alt.Tooltip("date", title=self.t.str_date, type="temporal")
                ]
            )
            .configure_legend(
                fillColor="white",
                strokeWidth=3,
                strokeColor="#f63366",
                cornerRadius=5,
                padding=10,
                orient=legend_position,
            )
            .configure_scale(continuousPadding=padding)
            .properties(width=width, height=height)
            .interactive()
        )

    def render_regions_choropleth(
        self,
        data: pd.DataFrame,
        topo_url: str,
        topo_feature: str,
        feature: str,
        title: str,
        width: int = 700,
        height: int = 1000,
    ) -> alt.Chart:
        regions_shape = alt.topo_feature(
            topo_url,
            topo_feature
        )
        chart_data = data[data[feature] > 0][[feature, "region_code"]]

        base_chart = (
            alt.Chart(regions_shape)
            .mark_geoshape(stroke="black", strokeWidth=0.5, color="white")
            .encode(tooltip=[alt.Tooltip("properties.reg_name:N",
                    title=title)])
        )

        color_chart = (
            alt.Chart(regions_shape)
            .mark_geoshape(stroke="black", strokeWidth=0.5)
            .encode(
                color=alt.Color(
                    f"{feature}:Q",
                    title=self.formatter(feature),
                    scale=alt.Scale(type="log", scheme="teals"),
                ),
                tooltip=[
                    alt.Tooltip("properties.reg_name:N", title=title),
                    alt.Tooltip(f"{feature}:Q", title=self.formatter(feature)),
                ],
            )
            .transform_lookup(
                "properties.reg_istat_code_num",
                from_=alt.LookupData(
                    data=chart_data, key="region_code", fields=[feature],
                ),
            )
        )

        final_chart = (
            (base_chart + color_chart)
            .configure_view(strokeWidth=0)
            .properties(width=width, height=height)
        )

        return final_chart
