import streamlit as st

from config import Config
from data import Data
from page import Page
from translation import Languages, Translate

langs = Languages()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=langs.get_array(), index=0)

config = Config()
t = Translate(language)

sources = config.get_sources_list()
source_options = config.get_opt_sources_list(t)
source_mapping = config.get_opt_sources_mapping(t)
source_selbox = st.sidebar.selectbox(
    label=t.label_source, options=source_options, index=0
)
source = source_mapping[source_selbox]
data = Data(source=source, lang=language)
if not data.data.empty:
    pages = [t.get(f'opt_page_{s}')
             for s in data.source_config.get('pages')]
    page_type = st.sidebar.selectbox(
        label=t.label_page, options=pages,
        index=0
    )
    page = Page(data, t)
    page_function_mapping = {
        t.opt_page_temporal_trend: page.line_plots,
        t.opt_page_geo_distribution: page.map_choropleth,
    }
    st.text(f"{t.str_latest_update}: {data.latest_update}")
    page_function_mapping[page_type]()

    if data.source_config.get("show_warnings", False):
        st.subheader(t.str_warnings)
        st.warning(t.get(f"warn_p_{source}_updates"))
    st.markdown(t.get(f"md_p_{source}_footer"))
    st.sidebar.title(t.sidebar_github)
else:
    st.error(t.error_source)
