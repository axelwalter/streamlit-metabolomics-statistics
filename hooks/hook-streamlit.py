from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata("streamlit")
datas += copy_metadata("plotly")
datas += copy_metadata("pingouin")
datas += copy_metadata("openpyxl")
datas += copy_metadata("kaleido")
datas += copy_metadata("scikit-posthocs")
datas += copy_metadata("gnpsdata")