import streamlit as st
from src.common import *
from src.cleanup import *


page_setup()

st.markdown("## Data Cleanup")

if st.session_state.ft.empty or st.session_state.md.empty:
    st.warning("Please select files for data clean up first!")
    st.experimental_rerun()

# clean up meta data table
md = clean_up_md(st.session_state.md)

# clean up feature table and remove unneccessary columns
ft = clean_up_ft(st.session_state.ft)

# # check if ft column names and md row names are the same
md, ft = check_columns(md, ft)

st.markdown("### Sample selection")
# Select true sample files (excluding blank and pools)
c1, c2 = st.columns(2)
md_inside = inside_levels(md)
show_table(
    md_inside,
    "Select samples (excluding blank and pools) based on the following table.",
    c1,
)
v_space(4, c2)
sample_column = c2.selectbox(
    "Choose attribute for sample selection",
    st.session_state.md.columns,
)
sample_row = c2.selectbox("Choose sample", set(st.session_state.md[sample_column]))
samples = ft[md[md[sample_column] == sample_row].index]
samples_md = md.loc[samples.columns]
with st.expander("**Selected samples**"):
    show_table(samples)

v_space(3)
st.markdown("### Blank removal")
# Ask if blank removal should be done
blank_removal = st.checkbox("Would you like to remove blank features?", False)
if blank_removal:
    non_samples_md = md.loc[
        [index for index in md.index if index not in samples.columns]
    ]
    c1, c2 = st.columns(2)
    show_table(
        inside_levels(non_samples_md),
        "Select blanks (excluding samples and pools) based on the following table.",
        c1,
    )
    v_space(4, c2)
    blank_column = c2.selectbox(
        "Choose attribute for blank selection", non_samples_md.columns
    )
    blank_row = c2.selectbox("Choose blank", set(non_samples_md[blank_column]))
    blanks = ft[non_samples_md[non_samples_md[blank_column] == blank_row].index]
    blanks_md = non_samples_md.loc[blanks.columns]
    with st.expander("**Selected blanks**"):
        show_table(blanks)

    # define a cutoff value for blank removal (ratio blank/avg(samples))
    st.markdown("##### Define a cutoff value for blank removal")
    c1, c2, c3 = st.columns(3)
    cutoff = c1.number_input(
        "recommended cutoff range between 0.1 and 0.3", 0.1, 1.0, 0.3, 0.05
    )
    blanks_removed, n_background_features, n_real_features = remove_blank_features(
        blanks, samples, cutoff
    )
    c2.metric("background or noise features", n_background_features)
    c3.metric("real features", n_real_features)
    with st.expander("**Feature table after removing blanks**"):
        show_table(blanks_removed)
    st.session_state["cutoff_LOD"] = get_cutoff_LOD(blanks_removed)
else:
    st.session_state["cutoff_LOD"] = get_cutoff_LOD(samples)

v_space(3)
st.markdown("### Imputation of missing values")
imputation = st.checkbox("Would you like to impute missing values?", False)
if imputation:
    if blank_removal:
        tmp_ft = blanks_removed
    else:
        tmp_ft = samples
    c1, c2 = st.columns(2)
    imputed = impute_missing_values(tmp_ft, get_cutoff_LOD(tmp_ft))
    with st.expander("**Imputed data**"):
        show_table(imputed)

v_space(3)
c1, c2 = st.columns(2)
if blank_removal:
    fig = get_feature_frequency_fig(blanks_removed)
else:
    fig = get_feature_frequency_fig(samples)
download_plotly_figure(fig, c1, "frequency-plot.png")
c1.plotly_chart(fig)

if imputation:
    fig = get_missing_values_per_feature_fig(imputed, st.session_state["cutoff_LOD"])
elif blank_removal:
    fig = get_missing_values_per_feature_fig(
        blanks_removed, st.session_state["cutoff_LOD"]
    )
else:
    fig = get_missing_values_per_feature_fig(samples, st.session_state["cutoff_LOD"])
download_plotly_figure(fig, c2, "missing-values-plot.png")
c2.plotly_chart(fig)

if imputation:
    st.session_state["ft_clean"] = imputed.T
elif blank_removal:
    st.session_state["ft_clean"] = blanks_removed.T
else:
    st.session_state["ft_clean"] = ft.T

st.session_state["md_clean"] = md

st.metric(
    f"Total missing values in dataset (coded as <= {st.session_state['cutoff_LOD']})",
    str(
        round(
            (
                (
                    st.session_state["ft_clean"] <= st.session_state["cutoff_LOD"]
                ).to_numpy()
            ).mean(),
            3,
        )
        * 100
    )
    + " %",
)
