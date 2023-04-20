import streamlit as st
from src.common import *
from src.clustering import *

page_setup()

st.markdown("# Hierachial Clustering & Heatmap")

with st.expander("About hierachial clustering and heatmaps"):
    st.markdown(
        """
Hierarchical clustering is a popular unsupervised machine learning technique used for grouping data points based on their similarities. In this method, the data is organized in a tree-like structure or dendrogram, where each branch represents a cluster of data points with similar features. The clustering process starts with each data point being considered as a separate cluster, and then iteratively combines similar clusters until all the data points are in a single cluster.

Heatmaps, on the other hand, are a graphical representation of data where the individual values are represented as colors. Heatmaps are often used in combination with hierarchical clustering to visualize the results of clustering analysis. The heatmap provides an easy-to-read visualization of the similarities and differences between the data points and clusters, with similar data points appearing as blocks of similar colors. Heatmaps are particularly useful for analyzing large datasets with complex relationships between variables.

There are a lot of [good videos](https://www.youtube.com/watch?v=7xHsRkOdVwo) and resources out there explaining very well the principle behind clustering. Some good ones are the following:
"""
    )
if not st.session_state.data.empty:
    t1, t2 = st.tabs(["Clustering", "Heatmap"])
    with t1:
        fig = get_dendrogram(st.session_state.data, "bottom")
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": [
                    "zoom",
                    "pan",
                    "select",
                    "lasso",
                    "zoomin",
                    "autoscale",
                    "zoomout",
                    "resetscale",
                ],
                "toImageButtonOptions": {"filename": "hierachiacal-clustering"},
            },
        )
    with t2:
        fig = get_heatmap(order_df_for_heatmap(st.session_state.data))
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": [
                    "zoom",
                    "pan",
                    "select",
                    "lasso",
                    "zoomin",
                    "autoscale",
                    "zoomout",
                    "resetscale",
                ],
                "toImageButtonOptions": {"filename": "heatmap"},
            },
        )

else:
    st.warning("Please complete data preparation step first!")
