import streamlit as st

from src.common import *
from src.ttest import *

page_setup()

st.markdown("# Student's t-test")

with st.expander("📖 Student's t-test"):
    st.markdown(
        "The Student's t-test is a statistical test used to determine whether the means of two groups of data are significantly different from each other. The t-test is a parametric test that assumes the data are normally distributed and the variances of the two groups are equal. It is commonly used in hypothesis testing to determine whether there is a significant difference between the means of two populations or to compare the means of two samples. The t-test is a powerful tool in statistical analysis and is often the go-to test for researchers and analysts when analyzing data."
    )

if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    c1.selectbox(
        "select attribute of interest",
        options=[
            c.replace("ATTRIBUTE_", "")
            for c in st.session_state.md.columns
            if len(set(st.session_state.md[c])) > 1
        ],
        key="ttest_attribute",
    )
    attribute_options = list(
        set(st.session_state.md["ATTRIBUTE_" + st.session_state.ttest_attribute])
    )
    attribute_options.sort()
    c2.multiselect(
        "select **two** options from the attribute for comparison",
        options=attribute_options,
        default=attribute_options[:2],
        key="ttest_options",
        max_selections=2,
        help="Select two options.",
    )
    c1.checkbox(
        "paired",
        False,
        key="ttest_paired",
        help="Specify whether the two observations are related (i.e. repeated measures) or independent.",
    )

    if c2.button("Run t-test", disabled=(len(st.session_state.ttest_options) != 2)):
        st.session_state.df_ttest = gen_ttest_data(
            "ATTRIBUTE_" + st.session_state.ttest_attribute,
            st.session_state.ttest_options,
            st.session_state.ttest_paired,
        )
        st.dataframe(st.session_state.df_ttest)

    if not st.session_state.df_ttest.empty:
        tabs = st.tabs(
            ["📈 Feature significance", "📊 Single metabolite plots", "📁 Data"]
        )

        with tabs[0]:
            fig = plot_ttest(st.session_state.df_ttest)
            show_fig(fig, "t-test")
        with tabs[1]:
            cols = st.columns(2)
            cols[0].selectbox(
                "metabolite", st.session_state.df_ttest.index, key="ttest_metabolite"
            )
            fig = ttest_boxplot(st.session_state.df_ttest,
                st.session_state.ttest_metabolite
            )
            show_fig(fig, f"ttest-boxplot-{st.session_state.ttest_metabolite}", False)

        with tabs[2]:
            show_table(st.session_state.df_ttest, "t-test-data")
