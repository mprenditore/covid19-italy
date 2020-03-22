import streamlit as st

from data import Data
from page import Page
from translation import Languages, Translate

langs = Languages()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=langs.get_array(), index=0)

data = Data(language)
t = Translate(language)

st.sidebar.title(t.title_page)
page = st.sidebar.selectbox(
    label=t.label_page, options=[t.opt_temporal_trend, t.opt_geo_distribution],
    index=0
)

st.text(f"{t.str_latest_update}: {data.latest_update}")

pages = Page(data, t)
page_function_mapping = {
    t.opt_temporal_trend: pages.line_plots,
    t.opt_geo_distribution: pages.map_choropleth,
}
page_function_mapping[page]()

st.subheader(t.str_warnings)
st.warning(t.warnings_updates)

st.markdown(t.md_footer)
st.sidebar.title(t.sidebar_github)
