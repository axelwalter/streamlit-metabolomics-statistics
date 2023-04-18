import streamlit as st
from src.common import *
from src.pcoa import *

page_setup()

st.markdown("# Multivariate Statistics")
st.markdown("### PERMANOVA & Principle Coordinate Analysis (PCoA)")

with st.expander("More information on PCoA", expanded=False):
    st.markdown(
        """
Principal coordinates analysis (PCoA) is a metric multidimensional scaling (MDS) method that attempts to represent sample dissimilarities in a low-dimensional space. It converts a distance st.session_state.pcoa_distance_matrix consisting of pair-wise distances (dissimilarities) across samples into a 2- or 3-D graph (Gower, 2005). Different distance metrics can be used to calculate dissimilarities among samples (e.g. Euclidean, Canberra, Minkowski). Performing a principal coordinates analysis using the Euclidean distance metric is the same as performing a principal components analysis (PCA). The selection of the most appropriate metric depends on the nature of your data and assumptions made by the metric.

Within the metabolomics field the Euclidean, Bray-Curtis, Jaccard or Canberra distances are most commonly used. The Jaccard distance is an unweighted metric (presence/absence) whereas Euclidean, Bray-Curtis and Canberra distances take into account relative abundances (weighted). Some metrics may be better suited for very sparse data (with many zeroes) than others. For example, the Euclidean distance metric is not recommended to be used for highly sparse data.

This [video tutorial](https://www.youtube.com/watch?v=GEn-_dAyYME) by StatQuest summarizes nicely the basic principles of PCoA. 
"""
    )

if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    c1.selectbox(
        "attribute for multivariate analysis",
        st.session_state.md.columns,
        key="pcoa_attribute",
    )
    c2.selectbox(
        "distance matrix",
        [
            "canberra",
            "chebyshev",
            "correlation",
            "cosine",
            "euclidean",
            "hamming",
            "jaccard",
            "matching",
            "minkowski",
            "seuclidean",
        ],
        key="pcoa_distance_matrix",
    )
    permanova, pcoa_result = permanova_pcoa(
        st.session_state.data,
        st.session_state.pcoa_distance_matrix,
        st.session_state.md[st.session_state.pcoa_attribute],
    )

    if not permanova.empty:
        t1, t2, t3 = st.tabs(
            [
                "PERMANOVA statistics",
                "Principle Coordinate Analysis",
                "Explained variance",
            ]
        )
        with t1:
            show_table(permanova, "PERMANOVA-statistics")
        with t2:
            fig = get_pcoa_scatter_plot(
                pcoa_result,
                st.session_state.md,
                st.session_state.pcoa_attribute,
            )
            st.plotly_chart(
                fig,
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": [
                        "lasso",
                        "select",
                        "resetscale",
                    ],
                    "toImageButtonOptions": {
                        "filename": f"PCoA-{st.session_state.pcoa_attribute}-{st.session_state.pcoa_distance_matrix}"
                    },
                },
            )
        with t3:
            fig = get_pcoa_variance_plot(pcoa_result)
            st.plotly_chart(
                fig,
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
                    "toImageButtonOptions": {
                        "filename": f"pcoa-explained-variance-{st.session_state.pcoa_distance_matrix}"
                    },
                },
            )

else:
    st.warning("Please complete data preparation step first!")
