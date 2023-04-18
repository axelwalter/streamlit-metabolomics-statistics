import streamlit as st
from .common import *

patterns = [
    ["m/z", "mz", "mass over charge"],
    ["rt", "retention time", "retention-time", "retention_time"],
]


def string_overlap(string, options):
    for option in options:
        if option in string and "mzml" not in string:
            return True
    return False


def get_new_index(df):
    # get m/z values (cols[0]) and rt values (cols[1]) column names
    cols = [
        [col for col in df.columns.tolist() if string_overlap(col.lower(), pattern)]
        for pattern in patterns
    ]
    try:
        # select the first match for each
        column_names = [col[0] for col in cols if col]
        if not column_names:
            return df, "no matching columns"
        # set metabolites column with index as default
        df["metabolite"] = df.index
        if len(column_names) == 2:
            df["metabolite"] = df[column_names[0]].round(5).astype(str)
            if column_names[1]:
                df["metabolite"] = (
                    df["metabolite"] + "@" + df[column_names[1]].round(2).astype(str)
                )
            if "row ID" in df.columns:
                df["metabolite"] = df["row ID"].astype(str) + "_" + df["metabolite"]
        df.set_index("metabolite", inplace=True)
    except:
        return df, "fail"
    return df, "success"


allowed_formats = "Allowed formats: csv (comma separated), tsv (tab separated), txt (tab separated), xlsx (Excel file)."


def load_example():
    ft = open_df("example-data/FeatureMatrix.csv")
    ft, _ = get_new_index(ft)
    md = open_df("example-data/MetaData.txt").set_index("filename")
    return ft, md


def load_ft(ft_file):
    ft = open_df(ft_file)
    # determining index with m/z, rt and adduct information
    if "metabolite" in ft.columns:
        ft.index = ft["metabolite"]
    else:
        v_space(2)
        st.warning(
            """⚠️ **Feature Table**

No **'metabolite'** column for unique metabolite ID specified.

Please select the correct one or try to automatically create an index based on RT and m/z values."""
        )
        c1, c2 = st.columns(2)
        metabolite_col = c1.selectbox(
            "Column to use for metabolite ID.",
            [col for col in ft.columns if not col.endswith("mzML")],
        )
        if metabolite_col:
            ft.index = ft[metabolite_col]
        v_space(2, c2)
        if c2.button("Create index automatically"):
            ft, msg = get_new_index(ft)
            if msg == "no matching columns":
                st.warning(
                    "Could not determine index automatically, missing m/z and/or RT information in column names."
                )
        v_space(2)
    if ft.empty:
        st.error(f"Check feature quantification table!\n{allowed_formats}")
    return ft


def load_md(md_file):
    md = open_df(md_file)
    # we need file names as index, if they don't exist throw a warning and let user chose column
    if "filename" in md.columns:
        md.set_index("filename", inplace=True)
    else:
        v_space(2)
        st.warning(
            """⚠️ **Meta Data Table**

No 'filename' column for samples specified.

Please select the correct one."""
        )
        filename_col = st.selectbox("Column to use for sample file names.", md.columns)
        if filename_col:
            md = md.set_index(filename_col)
        v_space(2)
    if md.empty:
        st.error(f"Check meta data table!\n{allowed_formats}")

    return md
