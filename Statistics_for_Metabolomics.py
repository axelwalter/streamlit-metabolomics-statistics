import streamlit as st
import pandas as pd
from src.utils import *
from src.stats import *
from src.visualizations import *

st.session_state.use_container_width = True
st.set_page_config(layout="wide")

st.session_state.md = pd.DataFrame()
st.session_state.ft = pd.DataFrame()
    
st.title("Statistics for Metabolomics")

