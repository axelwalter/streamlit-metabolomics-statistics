import streamlit as st
from src.common import *
from src.fileselection import *
from src.cleanup import *


page_setup()

st.markdown("# Data Preparation")

if st.session_state["data_preparation_done"]:
    st.success("Data preparation was successful!")
    if st.button("Re-do the data preparation step now."):
        st.session_state["md"], st.session_state["data"] = (
            pd.DataFrame(),
            pd.DataFrame(),
        )
        st.session_state["data_preparation_done"] = False
        st.experimental_rerun()
else:
    st.info(
        """💡 Once you are happy with the results, don't forget to click the **Submit Data for Statistics!** button."""
    )
    st.markdown("### File Upload")

    example = st.checkbox("Example Data")
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

    if not ft.empty or not md.empty:
        t1, t2 = st.tabs(["Feature Quantification", "Meta Data"])
        t1.dataframe(ft)
        t2.dataframe(md)

    if not ft.empty and not md.empty:
        st.success("Files loaded successfully!")
        st.markdown("### Data Cleanup")

        # clean up meta data table
        md = clean_up_md(md)

        # clean up feature table and remove unneccessary columns
        ft = clean_up_ft(ft)

        # # check if ft column names and md row names are the same
        md, ft = check_columns(md, ft)

        st.markdown("#### Blank removal")
        blank_removal = st.checkbox("Remove blank features?", False)
        if blank_removal:
            # Select true sample files (excluding blank and pools)
            st.markdown(
                "Select samples (excluding blank and pools) based on the following table."
            )
            st.dataframe(inside_levels(md))
            c1, c2 = st.columns(2)
            sample_column = c1.selectbox(
                "attribute for sample selection",
                md.columns,
            )
            sample_row = c2.selectbox("sample selection", set(md[sample_column]))
            samples = ft[md[md[sample_column] == sample_row].index]
            samples_md = md.loc[samples.columns]

            with st.expander(f"Selected samples {samples.shape}"):
                st.dataframe(samples)

            v_space(1)
            # Ask if blank removal should be done
            st.markdown(
                "Select blanks (excluding samples and pools) based on the following table."
            )
            non_samples_md = md.loc[
                [index for index in md.index if index not in samples.columns]
            ]
            st.dataframe(inside_levels(non_samples_md))
            c1, c2 = st.columns(2)

            blank_column = c1.selectbox(
                "attribute for blank selection", non_samples_md.columns
            )
            blank_row = c2.selectbox(
                "blank selection", set(non_samples_md[blank_column])
            )
            blanks = ft[non_samples_md[non_samples_md[blank_column] == blank_row].index]
            with st.expander(f"Selected blanks {blanks.shape}"):
                st.dataframe(blanks)

            # define a cutoff value for blank removal (ratio blank/avg(samples))
            c1, c2 = st.columns(2)
            cutoff = c1.number_input(
                "cutoff threshold for blank removal",
                0.1,
                1.0,
                0.3,
                0.05,
                help="""The recommended cutoff range is between 0.1 and 0.3.
                
Features with intensity ratio of (blank mean)/(sample mean) above the threshold (e.g. 30%) are considered noise/background features.
                """,
            )
            (
                ft,
                n_background_features,
                n_real_features,
            ) = remove_blank_features(blanks, samples, cutoff)
            c2.metric("background or noise features", n_background_features)
            with st.expander(f"Feature table after removing blanks {ft.shape}"):
                show_table(ft, "blank-features-removed")
        cutoff_LOD = get_cutoff_LOD(ft)

        st.markdown("##### Imputation")
        c1, c2 = st.columns(2)
        c2.metric(
            f"total missing values",
            str((ft == 0).to_numpy().mean() * 100)[:4] + " %",
            help=f"These values will be filled with random number between 0 and {cutoff_LOD} (Limit of Detection) during imputation.",
        )
        imputation = c1.checkbox("Impute missing values?", False)
        if imputation:
            c1, c2 = st.columns(2)
            ft = impute_missing_values(ft, cutoff_LOD)
            with st.expander(f"Imputed data {ft.shape}"):
                show_table(ft, "imputed")

        v_space(2)
        _, c1, _ = st.columns(3)
        if c1.button("**Submit Data for Statistics!**"):
            st.session_state["md"], st.session_state["data"] = transpose_and_scale(
                ft, md
            )
            st.session_state["data_preparation_done"] = True
            st.experimental_rerun()
        v_space(2)

        tab1, tab2 = st.tabs(
            ["Feature intensity frequency", "Missing values per feature"]
        )
        with tab1:
            fig = get_feature_frequency_fig(ft)
            show_fig(fig, "feature-intensity-frequency")
        with tab2:
            fig = get_missing_values_per_feature_fig(ft, cutoff_LOD)
            show_fig(fig, "missing-values")
