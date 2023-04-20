import streamlit as st
import pandas as pd

# significant_metabolites = ["13808_304.29997@8.64"]
# e1 = "A15M"
# e2 = "A45M"
# data = pd.concat(
#     [
#         st.session_state.data.loc[:, significant_metabolites],
#         st.session_state.md.loc[:, attribute],
#     ],
#     axis=1,
# )
# data = pd.concat([data[data[attribute] == e1], data[data[attribute] == e2]])
# st.write(data)

import pingouin as pg

attribute = "ATTRIBUTE_Sample"

df = pd.concat([st.session_state.md.loc[:, attribute], st.session_state.data])

pg.anova(data=df, dv="score", between="group")
