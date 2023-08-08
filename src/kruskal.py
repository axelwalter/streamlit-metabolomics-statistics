import streamlit as st
import pandas as pd
import numpy as np
import pingouin as pg
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import kruskal
import scikit_posthocs as sp

def gen_kruskal_data(group_data):
    for col in group_data[0].columns:
        statistic, p = kruskal(*[df[col] for df in group_data])
        yield col, p, statistic

def add_p_correction_to_kruskal(df, correction):
    # add Bonferroni corrected p-values for multiple testing correction
    if "p-corrected" not in df.columns:
        df.insert(2, "p-corrected",
                  pg.multicomp(df["p"].astype(float), method=correction)[1])
    # add significance
    if "significant" not in df.columns:
        df.insert(3, "significant", df["p-corrected"] < 0.05)
    # sort by p-value
    df.sort_values("p", inplace=True)
    return df


# @st.cache_data
def kruskal_wallis(df, attribute, correction):
    df = pd.concat([df, st.session_state.md], axis=1)
    groups = df[attribute].unique()
    group_data = [df[df[attribute] == group].drop(columns=[c for c in df.columns if "ATTRIBUTE_" in c]) for group in groups]

    df = pd.DataFrame(
        np.fromiter(
            gen_kruskal_data(group_data),
            dtype=[("metabolite", "U100"), ("p", "f"), ("statistic", "f")],
        )
    )
    df = df.dropna()
    df = add_p_correction_to_kruskal(df, correction)
    return df


@st.cache_resource
def get_kruskal_plot(kruskal):
    # first plot insignificant features
    fig = px.scatter(
        x=kruskal[kruskal["significant"] == False]["statistic"].apply(np.log),
        y=kruskal[kruskal["significant"] == False]["p"].apply(
            lambda x: -np.log(x)),
        template="plotly_white",
        width=600,
        height=600,
    )
    fig.update_traces(marker_color="#696880")

    # plot significant features
    fig.add_scatter(
        x=kruskal[kruskal["significant"]]["statistic"].apply(np.log),
        y=kruskal[kruskal["significant"]]["p"].apply(lambda x: -np.log(x)),
        mode="markers+text",
        text=kruskal["metabolite"].iloc[:6],
        textposition="top left",
        textfont=dict(color="#ef553b", size=14),
        name="significant",
    )

    fig.update_layout(
        font={"color": "grey", "size": 12, "family": "Sans"},
        title={
            "text": f"Kruskal Wallis - {st.session_state.kruskal_attribute.upper()}",
            "font_color": "#3E3D53"
        },
        xaxis_title="log(H)",
        yaxis_title="-log(p)",
        showlegend=False
    )

    return fig


@st.cache_resource
def get_metabolite_boxplot(kruskal, metabolite):
    attribute = "ATTRIBUTE_"+st.session_state.kruskal_attribute
    p_value = kruskal.set_index("metabolite")._get_value(metabolite, "p")
    df = pd.concat([st.session_state.data, st.session_state.md], axis=1)[
        [attribute, metabolite]
    ]
    title = f"{metabolite}<br>p-value: {str(p_value)[:6]}"
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
        dunn = pg.pairwise_tukey(df, dv=metabolite, between=attribute)
        yield (
            metabolite,
            dunn.loc[0, "diff"],
            dunn.loc[0, "p-tukey"],
            attribute.replace("ATTRIBUTE_", ""),
            dunn.loc[0, "A"],
            dunn.loc[0, "B"],
            dunn.loc[0, "mean(A)"],
            dunn.loc[0, "mean(B)"],
        )


def add_p_value_correction_to_dunns(dunn, correction):
    if "p-corrected" not in dunn.columns:
        # add Bonferroni corrected p-values
        dunn.insert(
            3, "p-corrected", pg.multicomp(
                dunn["stats_p"].astype(float), method=correction)[1]
        )
        # add significance
        dunn.insert(4, "stats_significant", dunn["p-corrected"] < 0.05)
        # sort by p-value
        dunn.sort_values("stats_p", inplace=True)
    return dunn


@st.cache_data
def dunn(df, attribute, elements, correction):
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
    dunn = dunn.dropna()
    dunn = add_p_value_correction_to_dunns(dunn, correction)
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
            y=df[df["stats_significant"]]["stats_p"].apply(
                lambda x: -np.log(x)),
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
            "text": f"dunn - {st.session_state.kruskal_attribute.upper()}: {st.session_state.dunn_elements[0]} - {st.session_state.dunn_elements[1]}",
            "font_color": "#3E3D53",
        },
        xaxis_title=f"diff",
        yaxis_title="-log(p)",
    )
    return fig
