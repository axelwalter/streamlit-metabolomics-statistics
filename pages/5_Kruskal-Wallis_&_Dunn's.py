import streamlit as st
from src.common import *
from src.kruskal import *


page_setup()

st.markdown("# Kruskal Wallis & Dunn's post hoc")

# with st.expander("📖 About"):
#     st.markdown(
#         """Analysis of variance (kruskal) is a statistical method used to compare means between two or more groups. kruskal tests whether there is a significant difference between the means of different groups based on the variation within and between groups. If kruskal reveals that there is a significant difference between at least two group means, post hoc tests are used to determine which specific groups differ significantly from one another. dunn's post hoc test is a widely used statistical method for pairwise comparisons after kruskal. It accounts for multiple comparisons and adjusts the p-values accordingly, allowing for a more accurate identification of significant group differences."""
#     )
#     st.image("assets/figures/kruskal.png")
#     st.image("assets/figures/dunns.png")

if not st.session_state.data.empty:
    c1, c2 = st.columns(2)
    c1.selectbox(
        "attribute for Kruskal Wallis test",
        options=[
            c.replace("ATTRIBUTE_", "")
            for c in st.session_state.md.columns
            if len(set(st.session_state.md[c])) > 1
        ],
        key="kruskal_attribute",
    )

    c1.button("Run Kruskal Wallis", key="run_kruskal")
    if st.session_state.run_kruskal:
        st.session_state.df_kruskal = kruskal(
            st.session_state.data,
            "ATTRIBUTE_" + st.session_state.kruskal_attribute,
            corrections_map[st.session_state.p_value_correction]
        )
        st.experimental_rerun()

    # if not st.session_state.df_kruskal.empty:
    #     attribute_options = list(
    #         set(st.session_state.md["ATTRIBUTE_" +
    #             st.session_state.kruskal_attribute].dropna())
    #     )
    #     attribute_options.sort()

    #     c2.multiselect(
    #         "select **two** options for Dunn's comparison",
    #         options=attribute_options,
    #         default=attribute_options[:2],
    #         key="dunn_elements",
    #         max_selections=2,
    #         help="Select two options.",
    #     )
    #     c2.button(
    #         "Run Dunn's",
    #         key="run_dunn",
    #         disabled=len(st.session_state.dunn_elements) != 2,
    #     )
    #     if st.session_state.run_dunn:
    #         st.session_state.df_dunn = dunn(
    #             st.session_state.df_kruskal,
    #             "ATTRIBUTE_" + st.session_state.kruskal_attribute,
    #             st.session_state.dunn_elements,
    #             corrections_map[st.session_state.p_value_correction]
    #         )
    #         st.experimental_rerun()

    tab_options = [
        "📈 Kruskal Wallis: plot",
        "📁 Kruskal Wallis: result table",
        "📊 Kruskal Wallis: significant metabolites",
    ]
    if not st.session_state.df_dunn.empty:
        tab_options += ["📈 Dunn's: plot", "📁 Dunn's: result"]

    if not st.session_state.df_kruskal.empty:
        tabs = st.tabs(tab_options)
        with tabs[0]:
            fig = get_kruskal_plot(st.session_state.df_kruskal)
            show_fig(fig, "kruskal")
        with tabs[1]:
            show_table(st.session_state.df_kruskal)
        with tabs[2]:
            c1, _ = st.columns(2)
            c1.selectbox(
                "select metabolite",
                sorted(
                    list(
                        st.session_state.df_kruskal["metabolite"][
                            st.session_state.df_kruskal["significant"] == True
                        ]
                    )
                ),
                key="kruskal_metabolite",
            )
            if st.session_state.kruskal_metabolite:
                fig = get_metabolite_boxplot(
                    st.session_state.df_kruskal,
                    st.session_state.kruskal_metabolite,
                )
                show_fig(fig, f"kruskal-{st.session_state.kruskal_metabolite}")

        if not st.session_state.df_dunn.empty:
            with tabs[3]:
                fig = get_dunn_volcano_plot(st.session_state.df_dunn)
                show_fig(fig, "dunns")
            with tabs[4]:
                show_table(st.session_state.df_dunn, "dunns")

else:
    st.warning(
        "Please complete data clean up step first! (Preparing data for statistical analysis)"
    )
