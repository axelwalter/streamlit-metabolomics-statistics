import streamlit as st
from src.common import *
from src.fileselection import *

page_setup()

st.markdown("## File Selection")


def example_data():
    if st.session_state.example:
        load_example()
    else:
        clear()


st.checkbox("**Example Data**", key="example", on_change=example_data)

if not st.session_state.example:
    c1, c2 = st.columns(2)
    # Feature Quantification Table
    c1.file_uploader("Feature Quantification Table", key="ft_file")
    if st.session_state.ft_file:
        st.session_state.ft = load_ft(st.session_state.ft_file)

    # Meta Data Table
    c2.file_uploader("Meta Data Table", key="md_file")
    if st.session_state.md_file:
        st.session_state.md = load_md(st.session_state.md_file)

if not st.session_state.ft.empty and not st.session_state.md.empty:
    st.success("Files loaded successfully!")

c1, c2 = st.columns(2)
if not st.session_state.ft.empty:
    show_table(st.session_state.ft, "Feature Quantification", c1)

if not st.session_state.md.empty:
    show_table(st.session_state.md, "Meta Data", c2)
