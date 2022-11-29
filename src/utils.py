import pandas as pd
import streamlit as st

####################
### common text ####
####################

allowed_formats = "Allowed formats: csv (comma separated), tsv (tab separated), txt (tab separated), xlsx (Excel file)."

#########################
### useful functions ####
#########################

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
        return df
    except:
        return pd.DataFrame()

def string_overlap(string, options):
    for option in options:
        if option in string and "mzml" not in string:
            return True
    return False

def table_title(df, title, col=""):
    text = f"##### {title}\n{df.shape[0]} rows, {df.shape[1]} columns"
    if col:
        return col.markdown(text)
    return st.markdown(text)

patterns = [
        ["m/z", "mz", "mass over charge"],
        ["rt", "retention time", "retention-time", "retention_time"]
    ]
def get_new_index(df, patterns):
    # get m/z values (cols[0]) and rt values (cols[1]) column names
    cols = [[col for col in df.columns.tolist() if string_overlap(col.lower(), pattern)] for pattern in patterns]
    try:
        # select the first match for each
        column_names = [col[0] for col in cols if col]
        # set metabolites column with index as default
        df["metabolites"] = df.index
        if len(column_names) == 2:
            df["metabolite"] = df[column_names[0]].round(4).astype(str)
            if column_names[1]:
                df["metabolite"] = df["metabolite"] + "@" + df[column_names[1]].round(1).astype(str)
        df.set_index("metabolite", inplace=True)
    except:
        pass
    return df

def inside_levels(df):
    # get all the columns (equals all attributes) -> will be number of rows
    levels = []
    types = []
    count = []
    for col in df.columns:
        types.append(type(df[col][0]))
        levels.append(sorted(set(df[col].dropna())))
        tmp = df[col].value_counts()
        count.append([tmp[levels[-1][i]] for i in range(len(levels[-1]))])
    return pd.DataFrame({"ATTRIBUTES": df.columns, "LEVELS": levels, "COUNT":count, "TYPES": types}, index=range(1, len(levels)+1))