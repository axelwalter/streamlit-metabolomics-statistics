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

def remove_blank_features(blanks, samples, cutoff):
    # Getting mean for every feature in blank and Samples
    avg_blank = blanks.mean(axis=1, skipna=False) # set skipna = False do not exclude NA/null values when computing the result.
    avg_samples = samples.mean(axis=1, skipna=False)

    # Getting the ratio of blank vs samples
    ratio_blank_samples = (avg_blank+1)/(avg_samples+1)

    # Create an array with boolean values: True (is a real feature, ratio<cutoff) / False (is a blank, background, noise feature, ratio>cutoff)
    is_real_feature = (ratio_blank_samples<cutoff)

    # Checking if there are any NA values present. Having NA values in the 4 variables will affect the final dataset to be created
    # temp_NA_Count = pd.concat([avg_blank, avg_samples, ratio_blank_samples, is_real_feature], 
    #                         keys=['avg_blank', 'avg_samples', 'ratio_blank_samples', 'bg_bin'], axis = 1)
    
    # print('No. of NA values in the following columns: ')
    # na_count_df = pd.DataFrame(temp_NA_Count.isna().sum(), columns=['NA'])

    # Calculating the number of background features and features present (sum(bg_bin) equals number of features to be removed)
    n_background = len(samples)-sum(is_real_feature)
    n_real_features = sum(is_real_feature)

    blank_removal = samples[is_real_feature.values]

    return blank_removal, n_background, n_real_features