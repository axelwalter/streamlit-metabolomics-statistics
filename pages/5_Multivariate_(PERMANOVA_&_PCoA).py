import streamlit as st
from src.stats import *
from src.utils import *
from src.visualizations import *

st.markdown("### Multivariate Statistics")
st.markdown("#### PERMANOVA & Principle Coordinate Analysis (PCoA)")

with st.expander("More information on PCoA", expanded=False):
    st.markdown("""
Principal coordinates analysis (PCoA) is a metric multidimensional scaling (MDS) method that attempts to represent sample dissimilarities in a low-dimensional space. It converts a distance matrix consisting of pair-wise distances (dissimilarities) across samples into a 2- or 3-D graph (Gower, 2005). Different distance metrics can be used to calculate dissimilarities among samples (e.g. Euclidean, Canberra, Minkowski). Performing a principal coordinates analysis using the Euclidean distance metric is the same as performing a principal components analysis (PCA). The selection of the most appropriate metric depends on the nature of your data and assumptions made by the metric.

Within the metabolomics field the Euclidean, Bray-Curtis, Jaccard or Canberra distances are most commonly used. The Jaccard distance is an unweighted metric (presence/absence) whereas Euclidean, Bray-Curtis and Canberra distances take into account relative abundances (weighted). Some metrics may be better suited for very sparse data (with many zeroes) than others. For example, the Euclidean distance metric is not recommended to be used for highly sparse data.

This [video tutorial](https://www.youtube.com/watch?v=GEn-_dAyYME) by StatQuest summarizes nicely the basic principles of PCoA. 
""")

if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    attribute = c1.selectbox("Attribute for multivariate analysis", [col for col in st.session_state.data.columns if (col.startswith("ATTRIBUTE_") and len(set(st.session_state.md.loc[st.session_state.scaled.index, col])) > 1)])
    matrix = c2.selectbox("distance matrix", ['canberra', 'chebyshev', 'correlation', 'cosine', 'euclidean', 'hamming', 'jaccard', 'matching', 'minkowski', 'seuclidean'])
    permanova, pcoa_result = permanova_pcoa(st.session_state.scaled, matrix, st.session_state.md.loc[st.session_state.scaled.index, attribute])
    
    if not permanova.empty:
        c1, c2 = st.columns(2)
        c1.markdown("#### PERMANOVA statistics:")
        c1.dataframe(permanova)
        c2.plotly_chart(get_pcoa_variance_plot(pcoa_result))
        st.plotly_chart(get_pcoa_scatter_plot(pcoa_result, st.session_state.md.loc[st.session_state.scaled.index], attribute))

else:
    st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")
