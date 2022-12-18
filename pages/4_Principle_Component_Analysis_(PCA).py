import streamlit as st
from src.stats import *
from src.utils import *
from src.visualizations import *


st.markdown("#### Principle Component Analysis (PCA)")
if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    n = c1.slider("number of components", 2, 10, 5)
    pca, pca_df = get_pca_df(st.session_state.scaled, n)
    st.dataframe(pca_df)
    st.plotly_chart(get_pca_scree_plot(pca_df, pca))
    attribute = st.selectbox("Attribute for PCA scatter plot", [col for col in st.session_state.data.columns if col.startswith("ATTRIBUTE_")])
    st.plotly_chart(get_pca_scatter_plot(pca_df, pca, attribute, st.session_state.md))
else:
    st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")