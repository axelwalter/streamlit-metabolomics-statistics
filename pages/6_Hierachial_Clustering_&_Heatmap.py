import streamlit as st
from src.common import *
from src.clustering import *

page_setup()

st.markdown("### Hierachial Clustering & Heatmap")

if not st.session_state.data.empty:
    with st.expander("Hierachial Clustering Algorithm"):
        st.markdown(
            """
The concept behind hierarchical clustering is to repeatedly combine the two nearest clusters into a larger cluster.

The first step consists of calculating the distance between every pair of observation points and stores it in a matrix.
1. It puts every point in its own cluster.
2. It merges the closest pairs of points according to their distances.
3. It recomputes the distance between the new cluster and the old ones and stores them in a new distance matrix.
4. It repeats steps 2 and 3 until all the clusters are merged into one single cluster.

There are a lot of good videos and resources out there explaining very well the principle behind clustering. Some good ones are the following:
- Hierarchical clustering and heatmaps: https://www.youtube.com/watch?v=7xHsRkOdVwo
"""
        )
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
