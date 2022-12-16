import streamlit as st
import pandas as pd
from src.utils import *
from src.stats import *
from src.visualizations import *

st.session_state.use_container_width = True
st.set_page_config(layout="wide")

st.session_state.md = pd.DataFrame()
st.session_state.ft = pd.DataFrame()
st.session_state.scaled = pd.DataFrame()
st.session_state.data = pd.DataFrame()
st.session_state.anova = pd.DataFrame()
st.session_state.tukeys = pd.DataFrame()

st.title("Statistics for Metabolomics")

st.markdown(
"""
## **About the different sections:**
### 1. File Selection
### 2. Data Cleanup

It involves cleaning the feature table, which contains all the features (metabolites) with their corresponding intensities. The data cleanup steps involved are: 1) Blank removal 2) Imputation 3) Normalisation 4) Scaling. Each step would be discussed in detail later. Once the data is cleaned, we can then use it for further statistical analyses.

### 3. Univariate statistical analysis

Here, we will use univariate statistical methods, such as ANOVA, to investigate whether there are differences in the levels of individual features between different time points in the dataset.

### 4. Unsupervised multivariate analyses:
#### i. PCoA and PERMANOVA
Here, we will perform a Principal Coordinate Analysis (PCoA), also known as metric or classical Multidimensional Scaling (metric MDS) to explore and visualize patterns in an untargeted mass spectromtery-based metabolomics dataset. We will then assess statistical significance of the patterns and dispersion of different sample types using permutational multivariate analysis of variance (PERMANOVA).

#### ii. Cluster Analyses and Heatmaps
We will also perform different cluster analyses to explore patterns in the data. This will help us to discover subgroups of samples or features that share a certain level of similarity. Clustering is an example of unsupervised learning where no labels are given to the learning algorithm which will try to find patterns/structures in the input data on its own. The goal of clustering is to find these hidden patterns.

Some types of cluster analyses (e.g. hierarchical clustering) are often associated with heatmaps. Heatmaps are a visual representation of the data where columns are usually samples and rows are features (in our case, different metabolic features). The color scale of heatmaps indicates higher or lower intensity (for instance, blue is lower and red is higher intensity).

There are a lot of good videos and resources out there explaining very well the principle behind clustering. Some good ones are the following:
- Hierarchical clustering and heatmaps: https://www.youtube.com/watch?v=7xHsRkOdVwo<br>
- K-means clustering: https://www.youtube.com/watch?v=4b5d3muPQmA
- ComplexHeatmap R package: https://jokergoo.github.io/ComplexHeatmap-reference/book/ 

### **5. Supervised multivariate analyses:**
we will perform a supervised analysis using XGBoost ....

---
"""
)