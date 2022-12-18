import streamlit as st
from src.stats import *
from src.utils import *
from src.visualizations import *

st.markdown("### Hierachial Clustering & Heatmap")

if not st.session_state.data.empty:
    with st.expander("Hierachial Clustering Algorithm"):
        st.markdown("""
The concept behind hierarchical clustering is to repeatedly combine the two nearest clusters into a larger cluster.

The first step consists of calculating the distance between every pair of observation points and stores it in a matrix.
1. It puts every point in its own cluster.
2. It merges the closest pairs of points according to their distances.
3. It recomputes the distance between the new cluster and the old ones and stores them in a new distance matrix.
4. It repeats steps 2 and 3 until all the clusters are merged into one single cluster.
""")
    label_pos = st.radio("dendrogram label position", ["bottom", "top"])
    st.plotly_chart(get_dendrogram(st.session_state.scaled, label_pos))
    st.plotly_chart(get_heatmap(order_df_for_heatmap(st.session_state.scaled)), use_container_width=True)

else:
    st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")