import streamlit as st
from src.common import *
from src.pca import *

page_setup()


st.markdown("#### Principle Component Analysis (PCA)")
if not st.session_state["scaled"].empty:
    c1, _, _ = st.columns(3)
    n = c1.number_input(
        "number of components", 2, st.session_state["scaled"].shape[0], 2
    )
    pca_variance, pca_df = get_pca_df(st.session_state["scaled"], n)
    with st.expander("**Principle components**"):
        show_table(pca_df)
    attribute = st.selectbox(
        "Attribute for PCA scatter plot",
        [
            column
            for column in st.session_state["data"].columns
            if "ATTRIBUTE" in column
        ],
    )
    c1, c2 = st.columns(2)
    fig = get_pca_scatter_plot(pca_df, pca_variance, attribute, st.session_state.md)
    c1.plotly_chart(fig)
    download_plotly_figure(fig, c1, filename="pca-variance.png")
    fig = get_pca_scree_plot(pca_df, pca_variance)
    c2.plotly_chart(fig)
    download_plotly_figure(fig, c2, filename="pca.png")
else:
    st.warning(
        "Please complete data clean up step first! (Preparing data for statistical analysis)"
    )
