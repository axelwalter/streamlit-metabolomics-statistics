import streamlit as st
import pandas as pd
from src.utils import *
from src.stats import *

st.set_page_config(layout="wide")
st.session_state.use_container_width = True
    
st.title("Statistics for Metabolomics")

# initialize empty feature table (ft) and meta data (md) dataframes
ft = pd.DataFrame()
md = pd.DataFrame()

# two column layout for file upload
c1, c2 = st.columns(2)
c1.markdown("##### Upload files or use example data")
use_example = c2.checkbox("Use Example Data", False)

# try to load feature table
featurematrix_file = c1.file_uploader("Feature Quantification Table")
if featurematrix_file:
    ft = open_df(featurematrix_file)
    # sometimes dataframes get saved with unnamed index, that needs to be removed
    if "Unnamed: 0" in ft.columns:
        ft.drop('Unnamed: 0', inplace=True, axis=1)
    # determining index with m/z, rt and adduct information
    ft = get_new_index(ft, patterns)
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
    ft = get_new_index(ft, patterns)
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
    v_space(3)

    st.markdown("### Data Cleanup")
    st.markdown("#### Sample selection")
    # clean up meta data table
    new_md = clean_up_md(md)

    # clean up feature table and remove unneccessary columns
    new_ft = clean_up_ft(ft)
    # table_title(new_ft, "Cleaned up Quantification Table")
    # st.dataframe(new_ft)

    # check if new_ft column names and md row names are the same
    st.markdown("##### Sanity check of sample names in meta data and feature table")
    new_md, new_ft = check_columns(new_md, new_ft)

    # Select true sample files (excluding blank and pools)
    c1, c2 = st.columns(2)
    table_title(inside_levels(new_md), "Select samples (excluding blank and pools) based on the following table.", c1)
    c1.dataframe(inside_levels(new_md))
    v_space(3, c2)
    sample_column = c2.selectbox("Choose attribute for sample selection", md.columns)
    sample_row = c2.selectbox("Choose sample", set(md[sample_column]))
    samples = new_ft[new_md[new_md[sample_column] == sample_row].index]
    samples_md = new_md.loc[samples.columns]
    table_title(samples, "Selected samples", c1)
    c1.write(samples)
    # table_title(samples_md, "Selected samples meta data", c2)
    # c2.write(samples_md)

    st.markdown("#### Blank removal")
    # Ask if blank removal should be done
    if st.checkbox("Would you like to remove blank features?", False):
        non_samples_md = new_md.loc[[index for index in new_md.index if index not in samples.columns]]
        c1, c2 = st.columns(2)
        table_title(inside_levels(non_samples_md), "Select blanks (excluding samples and pools) based on the following table.", c1)
        c1.dataframe(inside_levels(non_samples_md))
        v_space(3, c2)
        blank_column = c2.selectbox("Choose attribute for blank selection", non_samples_md.columns)
        blank_row = c2.selectbox("Choose blank", set(non_samples_md[blank_column]))
        blanks = new_ft[non_samples_md[non_samples_md[blank_column] == blank_row].index]
        blanks_md = non_samples_md.loc[blanks.columns]
        table_title(blanks, "Selected blanks", c1)
        c1.write(blanks)
        
        # define a cutoff value for blank removal (ratio blank/avg(samples))
        st.markdown("##### Define a cutoff value for blank removal")
        cutoff = st.number_input("recommended cutoff range between 0.1 and 0.3", 0.1, 1.0, 0.3, 0.05)
        blanks_removed, n_background_features, n_real_features = remove_blank_features(blanks, samples, cutoff)
        c1, c2 = st.columns(2)
        table_title(blanks_removed, "Feature table after removing blanks", c1)
        c1.dataframe(blanks_removed)
        v_space(10, c2)
        c2.metric("background or noise features", n_background_features)
        c2.metric("real features", n_real_features)