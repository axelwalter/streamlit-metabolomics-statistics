import streamlit as st
from src.utils import *
from src.stats import *
from src.visualizations import *

# initialize empty feature table (ft) and meta data (md) dataframes
ft = pd.DataFrame()
md = pd.DataFrame()

# two column layout for file upload
c1, c2 = st.columns(2)
c1.markdown("""
### File Selection
""")
# v_space(1, c2)
use_example = c2.checkbox("Use Example Data")
v_space(1, c2)
featurematrix_file = c1.file_uploader("Feature Quantification Table")
metadata_file = c2.file_uploader("Meta Data Table")


# if example files are used, overwrite tables with example data
if use_example:
    st.session_state.ft = open_df("example-data/FeatureMatrix.csv")
    st.session_state.ft, _ = get_new_index(st.session_state.ft)
    st.session_state.md = open_df("example-data/MetaData.txt").set_index("filename")
else:
    # try to load feature table
    # st.session_state.ft = pd.DataFrame()
    # st.session_state.md = pd.DataFrame()
    if featurematrix_file:
        ft = open_df(featurematrix_file)
        # sometimes dataframes get saved with unnamed index, that needs to be removed
        if "Unnamed: 0" in ft.columns:
            ft.drop('Unnamed: 0', inplace=True, axis=1)
        # determining index with m/z, rt and adduct information
        if "metabolite" in ft.columns:
            ft.index = ft["metabolite"]
        else:
            c1.warning("No 'metabolite' column for unique metabolite ID specified. Please select the correct one or try to automatically create an index based on RT and m/z values.")
            metabolite_col =  c1.selectbox("Column to use for metabolite ID.", [col for col in ft.columns if not col.endswith("mzML")])
            if metabolite_col:
                ft.index = ft[metabolite_col]
            if c1.button("Create index automatically"):
                ft, msg = get_new_index(ft)
                if msg == "no matching columns":
                    c1.error("Could not determine index automatically, missing m/z and/or RT information in column names.")
        if ft.empty:
            c1.error(f"Check feature quantification table!\n{allowed_formats}")
        else:
            st.session_state.ft = ft

    # try to load meta data table
    if metadata_file:
        md = open_df(metadata_file)
        # sometimes dataframes get saved with unnamed index, that needs to be removed
        if "Unnamed: 0" in md.columns:
            md.drop('Unnamed: 0', inplace=True, axis=1)
        # we need file names as index, if they don't exist throw a warning and let user chose column
        if "filename" in md.columns:
            md.set_index("filename", inplace=True)
        else:
            c2.warning("No 'filename' column for samples specified. Please select the correct one.")
            filename_col =  c2.selectbox("Column to use for sample file names.", md.columns)
            if filename_col:
                md.set_index(filename_col, inplace=True)
        if md.empty:
            c2.error(f"Check meta data table!\n{allowed_formats}")
        else:
            st.session_state.md = md

# display ft and md if they are selected
if not st.session_state.ft.empty:
    table_title(st.session_state.ft, "Feature Quantification", c1)
    c1.dataframe(st.session_state.ft)

if not st.session_state.md.empty:
    table_title(st.session_state.md, "Meta Data", c2)
    c2.dataframe(st.session_state.md)

if not st.session_state.ft.empty and not st.session_state.md.empty:
    st.success("Files loaded successfully!")
