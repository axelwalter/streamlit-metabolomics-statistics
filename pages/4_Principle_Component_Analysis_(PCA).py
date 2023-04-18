import streamlit as st
from src.common import *
from src.pca import *

page_setup()

# pd.concat([st.session_state.md, st.session_state.data], axis=1)

st.markdown("# Principle Component Analysis (PCA)")
if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    c1.number_input(
        "number of components",
        2,
        st.session_state.data.shape[0],
        2,
        key="n_components",
    )
    c2.selectbox(
        "attribute for PCA plot", st.session_state.md.columns, key="pca_attribute"
    )
    pca_variance, pca_df = get_pca_df(
        st.session_state.data, st.session_state.n_components
    )

    t1, t2, t3 = st.tabs(["PCA Plot", "Explained variance", "Data"])
    with t1:
        fig = get_pca_scatter_plot(
            pca_df, pca_variance, st.session_state.pca_attribute, st.session_state.md
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
                "toImageButtonOptions": {"filename": "pca"},
            },
        )
    with t2:
        fig = get_pca_scree_plot(pca_df, pca_variance)
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
                "toImageButtonOptions": {"filename": "pca-explainedvariance"},
            },
        )

    with t3:
        show_table(pca_df)
else:
    st.warning(
        "Please complete data clean up step first! (Preparing data for statistical analysis)"
    )
