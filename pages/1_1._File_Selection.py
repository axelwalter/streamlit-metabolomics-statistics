import streamlit as st
from src.utils import *
from src.stats import *
from src.visualizations import *

# initialize empty feature table (ft) and meta data (md) dataframes
ft = pd.DataFrame()
md = pd.DataFrame()

# two column layout for file upload
c1, c2 = st.columns(2)
c1.markdown("### Upload files or use example data")
v_space(1, c2)
use_example = c2.checkbox("Use Example Data", False)

# try to load feature table
featurematrix_file = c1.file_uploader("Feature Quantification Table")
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

# try to load meta data table
metadata_file = c2.file_uploader("Meta Data Table")
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

# if example files are used, overwrite tables with example data
if use_example:
    ft = open_df("example-data/FeatureMatrix.csv")
    ft, _ = get_new_index(ft)
    md = open_df("example-data/MetaData.txt").set_index("filename")

# display ft and md if they are selected
if not ft.empty:
    table_title(ft, "Feature Quantification", c1)
    c1.dataframe(ft)
if not md.empty:
    table_title(md, "Meta Data", c2)
    c2.dataframe(md)

if not ft.empty and not md.empty:
    st.success("Files loaded successfully!")
    st.session_state.md = md
    st.session_state.ft = ft
