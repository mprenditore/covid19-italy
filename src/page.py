import datetime
import altair as alt
import streamlit as st

from translation import Translate
from data import Data
from graph import Graph
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=60)


@cached(cache)
class Page:
    data = None
    source = None
    t = None
    graph = None
    data_rate = ""

    def __init__(self, data: Data, t: Translate):
        self.data = data
        self.t = t
        self.source = self.data.source
        self.graph = Graph(data, t)

    def dropdown_scale(self):
        st.markdown(self.t.md_data_to_visualize)
        features = self.data.features
        feature = st.selectbox(
            label=self.t.label_choose, options=features,
            index=self.data.source_config['def_feature_index'],
            format_func=self.graph.formatter
        )
        return feature

    def radio_scale(self, label: str, id: str):
        choice = st.radio(label=label, options=[
                self.t.opt_linear,
                self.t.opt_logarithmic],
                key=f"{label}_{id}_{self.source}")
        scale = (
            alt.Scale(type="symlog")
            if choice == self.t.opt_logarithmic
            else alt.Scale(type="linear")
        )
        return scale

    def radio_data_rate(self):
        data_rate = st.sidebar.radio(
                label=self.t.label_visualizations,
                options=[self.t.opt_total, self.t.opt_day_to_day])

        if data_rate == self.t.opt_total:
            self.data_rate = "total"
        else:
            if data_rate == self.t.opt_day_to_day:
                self.data_rate = "day-to-day"
        return self.data_rate

    def line_plots(self) -> None:
        """
        Render line plots.
        """
        national = self.data.aggregated_data

        st.title(self.t.get(f"title_p_{self.source}"))

        self.radio_data_rate()
        feature = self.dropdown_scale()

        # Group data by date and calculate log of interested feature

        # Choose log scale or linear, defines what feature to use
        national_scale = self.radio_scale(self.t.label_scale, 'global')

        st.header(self.t.get(f"md_p_{self.source}_aggregated_data"))
        suffix = "" if self.data_rate == "total" else "delta"

        national_chart = self.graph.render_global_chart(
            national, feature, suffix, national_scale, self.t.axis_month_day)
        st.altair_chart(national_chart)

        st.subheader(self.t.md_growth_factor)

        st.markdown(self.t.md_growth_factor_description_1)
        fraction = """
            $$
            \\frac{%s_{n+1}}{%s_{n}}
            $$
            """
        st.markdown(fraction % (self.t.str_cases, self.t.str_cases))
        st.markdown(self.t.md_growth_factor_description_2)

        suffix = "growth"

        national_growth_chart = self.graph.render_global_chart(
            national, feature, suffix, national_scale, self.t.axis_month_day)
        st.write(national_growth_chart)

        st.header(self.t.get(f"md_p_{self.source}_per_selected"))

        # Get list of regions and select the ones of interest
        region_options = self.data.regions_list
        regions = st.multiselect(
            label=self.t.label_regions,
            options=region_options,
            default=self.data.source_config['def_regions']
        )

        # Group data by date and region, sum up every feature,
        # filter ones in regions selection
        selected_regions = self.data.get_selected_regions_data(regions)

        regional_scale = self.radio_scale(self.t.label_scale, 'selected')

        suffix = "" if self.data_rate == "total" else "delta"

        st.subheader(self.t.get(f"md_p_{self.source}_selected_data"))

        if selected_regions.empty:
            st.warning(self.t.get(f"warn_p_{self.source}_no_sel_region"))
        else:
            regional_chart = self.graph.render_regional_chart(
                selected_regions, feature, suffix, regional_scale,
                self.t.axis_month_day, self.t.axis_region)
            st.write(regional_chart)

            suffix = "growth"
            st.subheader(self.t.md_growth_factor)
            regional_growth_chart = self.graph.render_regional_chart(
                selected_regions, feature, suffix, regional_scale,
                self.t.axis_month_day, self.t.axis_region,
                legend_position="bottom-left")
            st.write(regional_growth_chart)

    def map_choropleth(self) -> None:
        """
        Render chropleth of Italy with desired feature
        """

        topo_url = self.data.source_config['choropleth']['url']
        topo_feature = self.data.source_config['choropleth']['feature']

        st.title(self.t.get(f"title_p_{self.source}"))

        feature = self.dropdown_scale()

        # Date selection
        n_days = self.data.n_days
        st.markdown(self.t.md_elapsed_days)
        chosen_n_days = st.slider(
            label=self.t.label_days, min_value=0, max_value=n_days,
            value=n_days)
        chosen_date = datetime.date(2020, 2, 24) + datetime.timedelta(
            days=chosen_n_days)
        st.markdown(
            f"{self.t.str_chosen_date}: {chosen_date}"
        )
        filtered_data = self.data.get_on_days_passed(
            self.data.data, chosen_n_days)

        if filtered_data.empty:
            st.warning(self.t.warn_no_info_for_sel_date)
        else:
            choropleth = self.graph.render_regions_choropleth(
                filtered_data, topo_url, topo_feature, feature,
                self.t.axis_region)
            st.write(choropleth)
