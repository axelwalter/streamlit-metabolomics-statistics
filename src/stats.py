import streamlit as st
import pandas as pd

def clean_up_md(md):
    md = md.copy() #storing the files under different names to preserve the original files
    # remove the (front & tail) spaces, if any present, from the rownames of md
    md.index = [name.strip() for name in md.index]
    # for each col in md
    # 1) removing the spaces (if any)
    # 2) replace the spaces (in the middle) to underscore
    # 3) converting them all to UPPERCASE
    for col in md.columns:
        if md[col].dtype == str:
            md[col] = [item.strip().replace(" ", "_").upper() for item in md[col]]
    return md

def clean_up_ft(ft):
    ft = ft.copy() #storing the files under different names to preserve the original files
    # drop all columns that are not mzML or mzXML file names
    ft.drop(columns=[col for col in ft.columns if ".mz" not in col], inplace=True)
    # remove " Peak area" from column names
    ft.rename(columns={col: col.replace(" Peak area", "").strip() for col in ft.columns}, inplace=True)
    return ft

def check_columns(md, ft):
    if sorted(ft.columns) == sorted(md.index):
            st.success(f"All {len(ft.columns)} files are present in both meta data & feature table.")
    else:
        st.warning("Not all files are present in both meta data & feature table.")
        # print the md rows / ft column which are not in ft columns / md rows and remove them
        ft_cols_not_in_md = [col for col in ft.columns if col not in md.index]
        st.warning(f"These {len(ft_cols_not_in_md)} columns of feature table are not present in metadata table and will be removed:\n{', '.join(ft_cols_not_in_md)}")
        ft.drop(columns=ft_cols_not_in_md, inplace=True)
        md_rows_not_in_ft = [row for row in md.index if row not in ft.columns]
        st.warning(f"These {len(md_rows_not_in_ft)} rows of metadata table are not present in feature table and will be removed:\n{', '.join(md_rows_not_in_ft)}")
        md.drop(md_rows_not_in_ft, inplace=True)
    return md, ft