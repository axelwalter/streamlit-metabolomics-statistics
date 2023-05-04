import streamlit as st
import pandas as pd
import numpy as np
import pingouin as pg
import plotly.express as px
import plotly.graph_objects as go


def gen_kruwa_data(df, columns, groups_col):
    for col in columns:
        result = pg.kruskal(data=df, dv=col, between=groups_col, detailed=True).set_index(
            "Source"
        )
        p = result.loc[groups_col, "p-unc"]
        s = result.loc[groups_col, "H"]
        yield col, p, s


def add_bonferroni_to_kruwa(df):
    # add Bonferroni corrected p-values for multiple testing correction
    if "p-corrected" not in df.columns:
        df.insert(2, "p-corrected", pg.multicomp(df["p"], method=corrections_map[st.session_state.p_value_correction])[1])
    # add significance
    if "significant" not in df.columns:
        df.insert(3, "significant", df["p-corrected"] < 0.05)
    # sort by p-value
    df.sort_values("p", inplace=True)
    print("df shape: ")
    print(df.shape)
    return df


@st.cache_data
def kruwa(df, attribute):
    df = pd.DataFrame(
        np.fromiter(
            gen_kruwa_data(
                pd.concat([df, st.session_state.md], axis=1),
                df.columns,
                attribute,
            ),
            dtype=[("metabolite", "U100"), ("p", "f"), ("statistic", "f")],
        )
    )
    df = add_bonferroni_to_kruwa(df)
    return df


@st.cache_resource
def get_kruwa_plot(kruwa):
    # first plot insignificant features
    fig = px.scatter(
        x=kruwa[kruwa["significant"] == False]["statistic"].apply(np.log),
        y=kruwa[kruwa["significant"] == False]["p"].apply(lambda x: -np.log(x)),
        template="plotly_white",
        width=600,
        height=600,
    )
    fig.update_traces(marker_color="#696880")

    # plot significant features
    fig.add_scatter(
        x=kruwa[kruwa["significant"]]["statistic"].apply(np.log),
        y=kruwa[kruwa["significant"]]["p"].apply(lambda x: -np.log(x)),
        mode="markers+text",
        text=kruwa["metabolite"].iloc[:5],
        textposition="top left",
        textfont=dict(color="#ef553b", size=12),
        name="significant",
    )

    fig.update_layout(
        font={"color": "grey", "size": 12, "family": "Sans"},
        title={
            "text": f"Kruskall-Wallis - {st.session_state.kruwa_attribute.upper()}",
            "font_color": "#3E3D53",
        },
        xaxis_title="statistic",
        yaxis_title="-log(p)",
    )
    return fig


@st.cache_resource
def get_metabolite_boxplot(kruwa, metabolite):
    attribute = "ATTRIBUTE_"+st.session_state.kruwa_attribute
    p_value = kruwa.set_index("metabolite")._get_value(metabolite, "p")
    df = pd.concat([st.session_state.data, st.session_state.md], axis=1)[
        [attribute, metabolite]
    ]
    title = f"{metabolite}<br>p-value: {p_value}"
    fig = px.box(
        df,
        x=attribute,
        y=metabolite,
        template="plotly_white",
        width=800,
        height=600,
        points="all",
        color=attribute,
    )

    fig.update_layout(
        font={"color": "grey", "size": 12, "family": "Sans"},
        title={"text": title, "font_color": "#3E3D53"},
        xaxis_title=attribute.replace("ATTRIBUTE_", ""),
        yaxis_title="intensity",
    )
    return fig


def gen_pairwise_dunn(df, metabolites, attribute):
    """Yield results for pairwise dunn test for all metabolites between two options within the attribute."""
    for metabolite in metabolites:
        dunn = pg.pairwise_dunn(df, dv=metabolite, between=attribute)
        yield (
            metabolite,
            dunn.loc[0, "diff"],
            dunn.loc[0, "p-dunn"],
            attribute.replace("ATTRIBUTE_", ""),
            dunn.loc[0, "A"],
            dunn.loc[0, "B"],
            dunn.loc[0, "mean(A)"],
            dunn.loc[0, "mean(B)"],
        )


def add_bonferroni_to_dunns(dunn):
    if "stats_p-corrected" not in dunn.columns:
        # add Bonferroni corrected p-values
        dunn.insert(
            3, "stats_p-corrected", pg.multicomp(dunn["stats_p"], method=corrections_map[st.session_state.p_value_correction])[1]
        )
        # add significance
        dunn.insert(4, "stats_significant", dunn["stats_p-corrected"] < 0.05)
        # sort by p-value
        dunn.sort_values("stats_p", inplace=True)
    return dunn


@st.cache_data
def dunn(df, attribute, elements):
    significant_metabolites = df[df["significant"]]["metabolite"]
    data = pd.concat(
        [
            st.session_state.data.loc[:, significant_metabolites],
            st.session_state.md.loc[:, attribute],
        ],
        axis=1,
    )
    data = data[data[attribute].isin(elements)]
    dunn = pd.DataFrame(
        np.fromiter(
            gen_pairwise_dunn(data, significant_metabolites, attribute),
            dtype=[
                ("stats_metabolite", "U100"),
                (f"diff", "f"),
                ("stats_p", "f"),
                ("attribute", "U100"),
                ("A", "U100"),
                ("B", "U100"),
                ("mean(A)", "f"),
                ("mean(B)", "f"),
            ],
        )
    )
    dunn = add_bonferroni_to_dunns(dunn)
    return dunn


@st.cache_resource
def get_dunn_volcano_plot(df):
    # create figure
    fig = px.scatter(template="plotly_white")

    # plot insignificant values
    fig.add_trace(
        go.Scatter(
            x=df[df["stats_significant"] == False]["diff"],
            y=df[df["stats_significant"] == False]["stats_p"].apply(
                lambda x: -np.log(x)
            ),
            mode="markers",
            marker_color="#696880",
            name="insignificant",
        )
    )

    # plot significant values
    fig.add_trace(
        go.Scatter(
            x=df[df["stats_significant"]]["diff"],
            y=df[df["stats_significant"]]["stats_p"].apply(lambda x: -np.log(x)),
            mode="markers+text",
            text=df["stats_metabolite"].iloc[:5],
            textposition="top right",
            textfont=dict(color="#ef553b", size=12),
            marker_color="#ef553b",
            name="significant",
        )
    )

    fig.update_layout(
        font={"color": "grey", "size": 12, "family": "Sans"},
        title={
            "text": f"dunn - {st.session_state.kruwa_attribute.upper()}: {st.session_state.dunn_elements[0]} - {st.session_state.dunn_elements[1]}",
            "font_color": "#3E3D53",
        },
        xaxis_title=f"diff",
        yaxis_title="-log(p)",
    )
    return fig
