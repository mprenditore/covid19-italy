#!/usr/bin/env bash

mkdir -p ~/.streamlit/

echo -e "\
[general]\n\
email = \"${EMAIL}\"\n\
" > ~/.streamlit/credentials.toml

echo -e "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = ${PORT}\n\
" > ~/.streamlit/config.toml

streamlit run ${STREAMLIT_OPTIONS} COVID-19-Italy.py