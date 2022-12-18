import streamlit as st
from src.stats import *
from src.utils import *
from src.visualizations import *

st.markdown("### Multivariate Statistics: Cluster Analyses and Heatmaps")

if not st.session_state.data.empty:
    pass
else:
    st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")