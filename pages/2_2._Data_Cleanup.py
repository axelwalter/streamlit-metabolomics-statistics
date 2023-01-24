import streamlit as st
from src.utils import *
from src.stats import *
from src.visualizations import *

st.set_page_config(page_title="Statistics for Metabolomics", page_icon="src/icon.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

try:
    st.markdown("### Data Cleanup")

    if not st.session_state.ft.empty and not st.session_state.md.empty:
        st.markdown("#### Sample selection")
        # clean up meta data table
        new_md = clean_up_md(st.session_state.md)

        # clean up feature table and remove unneccessary columns
        new_ft = clean_up_ft(st.session_state.ft)
        # table_title(new_ft, "Cleaned up Quantification Table")
        # st.dataframe(new_ft)

        # check if new_ft column names and md row names are the same
        st.markdown("##### Sanity check of sample names in meta data and feature table")
        new_md, new_ft = check_columns(new_md, new_ft)

        # Select true sample files (excluding blank and pools)
        c1, c2 = st.columns(2)
        table_title(inside_levels(new_md), "Select samples (excluding blank and pools) based on the following table.", c1)
        c1.dataframe(inside_levels(new_md))
        v_space(7, c2)
        sample_column = c2.selectbox("Choose attribute for sample selection", st.session_state.md.columns)
        sample_row = c2.selectbox("Choose sample", set(st.session_state.md[sample_column]))
        samples = new_ft[new_md[new_md[sample_column] == sample_row].index]
        samples_md = new_md.loc[samples.columns]
        table_title(samples, "Selected samples", c1)
        st.write(samples)

        v_space(3)
        st.markdown("#### Blank removal")
        # Ask if blank removal should be done
        blank_removal = st.checkbox("Would you like to remove blank features?", False)
        if blank_removal:
            non_samples_md = new_md.loc[[index for index in new_md.index if index not in samples.columns]]
            c1, c2 = st.columns(2)
            table_title(inside_levels(non_samples_md), "Select blanks (excluding samples and pools) based on the following table.", c1)
            c1.dataframe(inside_levels(non_samples_md))
            v_space(7, c2)
            blank_column = c2.selectbox("Choose attribute for blank selection", non_samples_md.columns)
            blank_row = c2.selectbox("Choose blank", set(non_samples_md[blank_column]))
            blanks = new_ft[non_samples_md[non_samples_md[blank_column] == blank_row].index]
            blanks_md = non_samples_md.loc[blanks.columns]
            table_title(blanks, "Selected blanks", c1)
            st.write(blanks)
            
            # define a cutoff value for blank removal (ratio blank/avg(samples))
            st.markdown("##### Define a cutoff value for blank removal")
            c1, c2 = st.columns([0.30, 0.70])
            cutoff = c1.number_input("recommended cutoff range between 0.1 and 0.3", 0.1, 1.0, 0.3, 0.05)
            blanks_removed, n_background_features, n_real_features = remove_blank_features(blanks, samples, cutoff)
            c1, c2, c3 = st.columns(3)
            table_title(blanks_removed, "Feature table after removing blanks", c1)
            c2.metric("background or noise features", n_background_features)
            c3.metric("real features", n_real_features)
            st.dataframe(blanks_removed)
            cutoff_LOD = get_cutoff_LOD(blanks_removed)
        else:
            cutoff_LOD = get_cutoff_LOD(samples)


        v_space(3)
        st.markdown("#### Imputation of missing values")
        imputation = st.checkbox("Would you like to impute missing values?", False)
        if imputation:
            if blank_removal:
                tmp_ft = blanks_removed
            else:
                tmp_ft = samples
            c1, c2 = st.columns(2)
            table_title(tmp_ft, "Imputated data", c1)
            imputed = impute_missing_values(tmp_ft, get_cutoff_LOD(tmp_ft))
            st.dataframe(imputed)

        v_space(3)
        st.markdown("#### Normalization")
        normalization = st.checkbox("Would you like to normalize values column-wise (sample centric)?", False)
        if normalization:
            if imputation:
                tmp_ft = imputed
            elif blank_removal:
                tmp_ft = blanks_removed
            else:
                tmp_ft = samples
            normalized = normalize_column_wise(tmp_ft)
            c1, c2 = st.columns(2)
            table_title(normalized, "Normalized data", c1)
            st.dataframe(normalized)

        v_space(3)
        c1, c2 = st.columns(2)
        if blank_removal:
            fig = get_feature_frequency_fig(blanks_removed)
        else:
            fig = get_feature_frequency_fig(samples)
        download_plotly_figure(fig, c1, "frequency-plot.svg")
        c1.plotly_chart(fig)

        if imputation:
            fig = get_missing_values_per_feature_fig(imputed, cutoff_LOD)
        elif blank_removal:
            fig = get_missing_values_per_feature_fig(blanks_removed, cutoff_LOD)
        else:
            fig = get_missing_values_per_feature_fig(samples, cutoff_LOD)
        download_plotly_figure(fig, c2, "missing-values-plot.svg")
        c2.plotly_chart(fig)


        v_space(3)
        st.markdown("""#### Preparing data for statistical analysis
For statistical analysis data needs to be transposed (samples as rows) as well as scaled and centered (around zero).
Features with more then 50% missing values will be removed.
    """)
        _, c2, _ = st.columns([0.3, 0.4, 0.3])
        if c2.button("**Prepare data for statistical analysis now!**"):
            with st.spinner("Transposing and scaling data..."):
                # transposing tables already
                if imputation:
                    tmp_ft = imputed.T
                elif blank_removal:
                    tmp_ft = blanks_removed.T
                else:
                    tmp_ft = new_ft.T

                st.session_state.scaled, st.session_state.data = transpose_and_scale(tmp_ft, new_md, cutoff_LOD)
                st.success("Your data is now ready for statistical analysis!")
        
        if not st.session_state.data.empty:
            c1, c2 = st.columns(2)
            table_title(st.session_state.data, "Scaled feature table for statistical analysis", c1)
            st.dataframe(st.session_state.data)
    else:
        st.warning("Please select files for data clean up first!")

except:
    st.warning("Something went wrong.")