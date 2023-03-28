import streamlit as st
import pandas as pd
import io
import uuid
from sklearn.preprocessing import StandardScaler


def page_setup():
    # streamlit configs
    st.set_page_config(
        page_title="Statistics for Metabolomics",
        page_icon="assets/icon.png",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    # initialize global session state variables if not already present
    # DataFrames
    for key in ("ft", "md"):
        if key not in st.session_state:
            st.session_state[key] = pd.DataFrame()


def v_space(n, col=None):
    for _ in range(n):
        if col:
            col.write("")
        else:
            st.write("")


def open_df(file):
    separators = {"txt": "\t", "tsv": "\t", "csv": ","}
    try:
        if type(file) == str:
            ext = file.split(".")[-1]
            if ext != "xlsx":
                df = pd.read_csv(file, sep=separators[ext])
            else:
                df = pd.read_excel(file)
        else:
            ext = file.name.split(".")[-1]
            if ext != "xlsx":
                df = pd.read_csv(file, sep=separators[ext])
            else:
                df = pd.read_excel(file)
        # sometimes dataframes get saved with unnamed index, that needs to be removed
        if "Unnamed: 0" in df.columns:
            df.drop("Unnamed: 0", inplace=True, axis=1)
        return df
    except:
        return pd.DataFrame()


def show_table(df, title="", col=""):
    if col:
        col = col
    else:
        col = st
    if title:
        col.markdown(f"**{title}**")
    col.download_button(
        f"{df.shape[0]} rows, {df.shape[1]} columns",
        df.to_csv(sep="\t").encode("utf-8"),
        title.replace(" ", "-") + ".tsv",
        key=uuid.uuid1(),
    )
    col.dataframe(df)


def download_plotly_figure(fig, col=None, filename=""):
    buffer = io.BytesIO()
    fig.write_image(file=buffer, format="png")

    if col:
        col.download_button(
            label=f"Download Figure",
            data=buffer,
            file_name=filename,
            mime="application/png",
        )
    else:
        st.download_button(
            label=f"Download Figure",
            data=buffer,
            file_name=filename,
            mime="application/png",
        )


@st.cache_data
def transpose_and_scale(feature_df, meta_data_df, cutoff_LOD):
    # remove meta data rows that are not samples
    md_rows_not_in_samples = [
        row for row in meta_data_df.index if row not in feature_df.index
    ]
    md_samples = meta_data_df.drop(md_rows_not_in_samples)

    # put the rows in the feature table and metadata in the same order
    feature_df.sort_index(inplace=True)
    md_samples.sort_index(inplace=True)

    try:
        if not list(set(md_samples.index == feature_df.index))[0] == True:
            st.warning("Sample names in feature and metadata table are NOT the same!")
    except:
        st.warning(
            "Sample names in feature and metadata table can NOT be compared. Please check your tables!"
        )

    scaled = pd.DataFrame(
        StandardScaler().fit_transform(feature_df),
        index=feature_df.index,
        columns=feature_df.columns,
    )
    data = pd.merge(md_samples, scaled, left_index=True, right_index=True, how="inner")
    # scale and return
    return data, scaled
