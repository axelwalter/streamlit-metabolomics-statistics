import pandas as pd

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

patterns = [
        ["m/z", "mz", "mass over charge"],
        ["RT", "retention time", "retention-time", "retention_time"]
    ]
def get_new_index(df, patterns):
    # get m/z values (cols[0]) and rt values (cols[1]) column names
    cols = [[col for col in df.columns.tolist() if string_overlap(col.lower(), pattern)] for pattern in patterns]
    # select the first match for each
    column_names = [col[0] for col in cols if cols]
    # set metabolites column with index as default
    df["metabolites"] = df.index
    if len(column_names) == 2:
        df["metabolite"] = df[column_names[0]].round(4).astype(str)
        if column_names[1]:
            df["metabolite"] = df["metabolite"] + "@" + df[column_names[1]].round(1).astype(str)
    df.set_index("metabolite", inplace=True)
    return df
