import streamlit as st

if not st.session_state.scaled.empty:
    pass
else:
    st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")