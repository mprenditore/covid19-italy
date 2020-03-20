import streamlit as st

from data import Data
from page import Page
from translation import Languages, Translate

langs = Languages()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=langs.get_array(), index=1)

data = Data(language)
t = Translate(language)

st.sidebar.title(t.title_page)
page = st.sidebar.selectbox(
    label=t.label_page, options=[t.opt_temporal_trend, t.opt_geo_distribution],
    index=0
)

st.sidebar.title(t.title_visualizations)
st.sidebar.markdown(t.md_visualizations_description)
data_rate = st.sidebar.radio(label=t.label_visualizations,
                             options=[t.opt_total, t.opt_day_to_day])
st.sidebar.title(t.sidebar_github)

if data_rate == t.opt_total:
    data_rate = "total"
else:
    if data_rate == t.opt_day_to_day:
        data_rate = "day-to-day"

pages = Page(data, t, mode=data_rate)
page_function_mapping = {
    t.opt_temporal_trend: pages.line_plots,
    t.opt_geo_distribution: pages.map_choropleth,
}
page_function_mapping[page]()
# page_function_mapping[page](data=data, t=t, mode=data_rate)

st.subheader(t.str_warnings)
st.warning(t.warnings_updates)

st.markdown(t.md_footer)
