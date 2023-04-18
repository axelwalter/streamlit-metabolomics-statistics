import streamlit as st
from src.common import *
from src.fileselection import *
from src.cleanup import *


page_setup()

st.markdown("# Data Preparation")

if not st.session_state["md"].empty and not st.session_state["data"].empty:
    st.info("💡 You have already prepared data for statistical analysis.")
    if st.button("Re-do the data preparation step now."):
        st.session_state["md"], st.session_state["data"] = (
            pd.DataFrame(),
            pd.DataFrame(),
        )
        st.experimental_rerun()
else:
    st.markdown("## File Upload")

    example = st.checkbox("**Example Data**")
    if example:
        ft, md = load_example()
    else:
        ft, md = pd.DataFrame(), pd.DataFrame()

    if not example:
        c1, c2 = st.columns(2)
        # Feature Quantification Table
        ft_file = c1.file_uploader("Feature Quantification Table")
        if ft_file:
            ft = load_ft(ft_file)

        # Meta Data Table
        md_file = c2.file_uploader("Meta Data Table")
        if md_file:
            md = load_md(md_file)

    c1, c2 = st.columns(2)
    if not ft.empty:
        show_table(ft, "Feature Quantification", c1)

    if not md.empty:
        show_table(md, "Meta Data", c2)

    if not ft.empty and not md.empty:
        st.success("Files loaded successfully!")
        st.markdown("## Data Cleanup")

        # clean up meta data table
        md = clean_up_md(md)

        # clean up feature table and remove unneccessary columns
        ft = clean_up_ft(ft)

        # # check if ft column names and md row names are the same
        md, ft = check_columns(md, ft)

        # Select true sample files (excluding blank and pools)
        st.markdown(
            "Select samples (excluding blank and pools) based on the following table."
        )
        st.dataframe(inside_levels(md))
        c1, c2 = st.columns(2)
        sample_column = c1.selectbox(
            "Choose attribute for sample selection",
            md.columns,
        )
        sample_row = c2.selectbox("Choose sample", set(md[sample_column]))
        samples = ft[md[md[sample_column] == sample_row].index]
        samples_md = md.loc[samples.columns]

        with st.expander(f"**Selected samples {samples.shape}**"):
            st.dataframe(samples)

        v_space(1)
        # Ask if blank removal should be done
        blank_removal = st.checkbox("**Remove blank features?**", False)
        if blank_removal:
            st.markdown(
                "Select blanks (excluding samples and pools) based on the following table."
            )
            non_samples_md = md.loc[
                [index for index in md.index if index not in samples.columns]
            ]
            st.dataframe(inside_levels(non_samples_md))
            c1, c2 = st.columns(2)

            blank_column = c1.selectbox(
                "Choose attribute for blank selection", non_samples_md.columns
            )
            blank_row = c2.selectbox("Choose blank", set(non_samples_md[blank_column]))
            blanks = ft[non_samples_md[non_samples_md[blank_column] == blank_row].index]
            blanks_md = non_samples_md.loc[blanks.columns]
            with st.expander(f"**Selected blanks {blanks.shape}**"):
                st.dataframe(blanks)

            # define a cutoff value for blank removal (ratio blank/avg(samples))
            st.markdown("**Define a cutoff value for blank removal.**")
            c1, c2, c3 = st.columns(3)
            cutoff = c1.number_input(
                "recommended cutoff range between 0.1 and 0.3", 0.1, 1.0, 0.3, 0.05
            )
            (
                blanks_removed,
                n_background_features,
                n_real_features,
            ) = remove_blank_features(blanks, samples, cutoff)
            c2.metric("background or noise features", n_background_features)
            c3.metric("real features", n_real_features)
            with st.expander(
                f"**Feature table after removing blanks {blanks_removed.shape}**"
            ):
                show_table(blanks_removed)
            cutoff_LOD = get_cutoff_LOD(blanks_removed)
        else:
            cutoff_LOD = get_cutoff_LOD(samples)

        v_space(1)
        imputation = st.checkbox("**Impute missing values?**", False)
        if imputation:
            if blank_removal:
                tmp_ft = blanks_removed
            else:
                tmp_ft = samples
            c1, c2 = st.columns(2)
            imputed = impute_missing_values(tmp_ft, get_cutoff_LOD(tmp_ft))
            with st.expander(f"**Imputed data {imputed.shape}**"):
                show_table(imputed)

        if imputation:
            ft_clean = imputed.T
        elif blank_removal:
            ft_clean = blanks_removed.T
        else:
            ft_clean = ft.T

        v_space(1)
        st.session_state["md"], st.session_state["data"] = transpose_and_scale(
            ft_clean, md
        )
        if not st.session_state["data"].empty:
            st.success("Data clean-up successful!")

        st.metric(
            f"Total missing values in dataset (coded as <= {cutoff_LOD})",
            str(
                round(
                    ((ft_clean <= cutoff_LOD).to_numpy()).mean(),
                    3,
                )
                * 100
            )
            + " %",
        )

        if blank_removal:
            fig = get_feature_frequency_fig(blanks_removed)
        else:
            fig = get_feature_frequency_fig(samples)
        download_plotly_figure(fig, "frequency-plot.png")
        st.plotly_chart(fig)

        if imputation:
            fig = get_missing_values_per_feature_fig(imputed, cutoff_LOD)
        elif blank_removal:
            fig = get_missing_values_per_feature_fig(blanks_removed, cutoff_LOD)
        else:
            fig = get_missing_values_per_feature_fig(samples, cutoff_LOD)
        download_plotly_figure(fig, "missing-values-plot.png")
        st.plotly_chart(fig)
