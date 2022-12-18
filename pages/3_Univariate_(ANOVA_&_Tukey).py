import streamlit as st
from src.stats import *
from src.utils import *
from src.visualizations import get_anova_plot, get_tukey_volcano_plot, get_metabolite_boxplot

st.markdown("### Univariate Statistics")

if not st.session_state.data.empty:
    st.markdown("#### ANOVA")
    c1, c2 = st.columns(2)
    attribute = c1.selectbox("Attribute for ANOVA test", [col for col in st.session_state.data.columns if col.startswith("ATTRIBUTE_")])
    v_space(2, c2)
    if c2.button("Run ANOVA"):
        with st.spinner(f"Running ANOVA based on {attribute}..."):
            dtypes = [('metabolite', 'U100'), ('p', 'f'), ('F', 'f')]
            anova = pd.DataFrame(np.fromiter(gen_anova_data(st.session_state.data, st.session_state.scaled.columns, attribute), dtype=dtypes))
            st.session_state.anova = add_bonferroni_to_anova(anova)

    if not st.session_state.anova.empty:
        v_space(2)
        table_title(st.session_state.anova, "ANOVA results table")
        st.dataframe(st.session_state.anova) 
        c1, c2 = st.columns([0.6, 0.4])
        c1.plotly_chart(get_anova_plot(st.session_state.anova))

    v_space(2)
    if not st.session_state.anova.empty:
        st.markdown("##### Inspect single significant metabolites")
        metabolite = st.selectbox("Select metabolite", sorted(list(st.session_state.anova["metabolite"][st.session_state.anova["significant"]==True])))
        st.plotly_chart(get_metabolite_boxplot(st.session_state.anova, st.session_state.data, metabolite))

    v_space(2)
    st.markdown("#### Tukey's post hoc test")
    st.markdown("Choose elements of the selected attribute for comparison.")
    c1, c2, c3 = st.columns(3)
    e1 = c1.selectbox("Element 1", set(st.session_state.data[attribute]))
    e2 = c2.selectbox("Element 2", set(st.session_state.data[attribute]))
    elements = [e1, e2]
    v_space(2, c3)
    if c3.button("Run Tukey's"):
        if not st.session_state.anova.empty:
            with st.spinner(f"Running Tukey's post hoc test between {attribute} {e1} and {e2}..."):
                dtypes = [('stats_metabolite', 'U100'), ('stats_diff', 'f'), ('stats_p', 'f')]
                tukey = pd.DataFrame(np.fromiter(gen_pairwise_tukey(st.session_state.data, elements, st.session_state.anova[st.session_state.anova['significant']]['metabolite']), dtype=dtypes))

                st.session_state.tukeys = add_bonferroni_to_tukeys(tukey)

        else:
            st.warning("Run ANOVA before Tukey's post hoc test.")

    if not st.session_state.tukeys.empty:
        st.dataframe(st.session_state.tukeys)
        c1, c2 = st.columns([0.7, 0.3])
        c1.plotly_chart(get_tukey_volcano_plot(st.session_state.tukeys))

else:
    st.warning("Please complete data clean up step first! (Preparing data for statistical analysis)")