import streamlit as st
from src.stats import *
from src.utils import *
from src.visualizations import *

st.set_page_config(page_title="Statistics for Metabolomics", page_icon="src/icon.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

try:
    st.markdown("#### Principle Component Analysis (PCA)")
    if not st.session_state.data.empty:
        c1, c2 = st.columns(2)
        n = c1.slider("number of components", 2, st.session_state.scaled.shape[0], 5)
        pca, pca_df = get_pca_df(st.session_state.scaled, n)
        st.dataframe(pca_df)
        attribute = st.selectbox("Attribute for PCA scatter plot", [col for col in st.session_state.data.columns if col.startswith("ATTRIBUTE_")])
        c1, c2 = st.columns(2)
        fig = get_pca_scatter_plot(pca_df, pca, attribute, st.session_state.md)
        download_plotly_figure(fig, c1, filename="pca-variance.svg")
        c1.plotly_chart(fig)
        fig = get_pca_scree_plot(pca_df, pca)
        download_plotly_figure(fig, c2, filename="pca.svg")
        c2.plotly_chart(fig)
    else:
        st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")

except:
    st.warning("Something went wrong.")