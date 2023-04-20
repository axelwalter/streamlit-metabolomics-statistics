import streamlit as st
from src.common import *
from src.anova import *


page_setup()

st.markdown("# ANOVA & Tukey's post hoc test")

with st.expander("📖 ANOVA and Tukey's post hoc test"):
    st.markdown(
        """Analysis of variance (ANOVA) is a statistical method used to compare means between two or more groups. ANOVA tests whether there is a significant difference between the means of different groups based on the variation within and between groups. If ANOVA reveals that there is a significant difference between at least two group means, post hoc tests are used to determine which specific groups differ significantly from one another. Tukey's post hoc test is a widely used statistical method for pairwise comparisons after ANOVA. It accounts for multiple comparisons and adjusts the p-values accordingly, allowing for a more accurate identification of significant group differences."""
    )

if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    c1.selectbox(
        "attribute for ANOVA test",
        options=[
            c.replace("ATTRIBUTE_", "")
            for c in st.session_state.md.columns
            if len(set(st.session_state.md[c])) > 1
        ],
        key="anova_attribute",
    )

    c1.button("Run ANOVA", key="run_anova")
    if st.session_state.run_anova:
        st.session_state.df_anova = anova(
            "ATTRIBUTE_" + st.session_state.anova_attribute
        )

    if not st.session_state.df_anova.empty:
        attribute_options = list(
            set(st.session_state.md["ATTRIBUTE_" + st.session_state.anova_attribute])
        )
        attribute_options.sort()

        c2.multiselect(
            "select **two** options for Tukey's comparison",
            options=attribute_options,
            default=attribute_options[:2],
            key="tukey_elements",
            max_selections=2,
            help="Select two options.",
        )
        c2.button(
            "Run Tukey's",
            key="run_tukey",
            disabled=len(st.session_state.tukey_elements) != 2,
        )
        if st.session_state.run_tukey:
            st.session_state.df_tukey = tukey(
                st.session_state.df_anova[st.session_state.df_anova["significant"]][
                    "metabolite"
                ],
                "ATTRIBUTE_" + st.session_state.anova_attribute,
                st.session_state.tukey_elements,
            )

    tab_options = [
        "📈 ANOVA: plot",
        "📁 ANOVA: result table",
        "📊 ANOVA: significant metabolites",
    ]
    if not st.session_state.df_tukey.empty:
        tab_options += ["Tukey's: plot", "Tukey's: result"]
    tabs = st.tabs(tab_options)

    if not st.session_state.df_anova.empty:
        with tabs[0]:
            fig = get_anova_plot(st.session_state.df_anova)
            show_fig(fig, "anova")
        with tabs[1]:
            show_table(st.session_state.df_anova)
        with tabs[2]:
            c1, _ = st.columns(2)
            c1.selectbox(
                "select metabolite",
                sorted(
                    list(
                        st.session_state.df_anova["metabolite"][
                            st.session_state.df_anova["significant"] == True
                        ]
                    )
                ),
                key="anova_metabolite",
            )
            fig = get_metabolite_boxplot(
                st.session_state.df_anova,
                st.session_state.anova_metabolite,
                "ATTRIBUTE_" + st.session_state.anova_attribute,
            )
            show_fig(fig, f"anova-{st.session_state.anova_metabolite}")

        if not st.session_state.df_tukey.empty:
            with tabs[3]:
                fig = get_tukey_volcano_plot(st.session_state.df_tukey)
                show_fig(fig, "tukeys")
            with tabs[4]:
                show_table(st.session_state.df_tukey)

else:
    st.warning(
        "Please complete data clean up step first! (Preparing data for statistical analysis)"
    )
