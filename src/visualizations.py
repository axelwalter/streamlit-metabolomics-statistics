import plotly.express as px
import pandas as pd
import numpy as np

def get_feature_frequency_fig(df):
    bins, bins_label, a = [-1, 0, 1, 10], ['-1','0', "1", "10"], 2

    while a<=10:
        bins_label.append(np.format_float_scientific(10**a))
        bins.append(10**a)
        a+=1

    freq_table = pd.DataFrame(bins_label)
    frequency = pd.DataFrame(np.array(np.unique(np.digitize(df.to_numpy(), bins, right=True), return_counts=True)).T).set_index(0)
    freq_table = pd.concat([freq_table,frequency], axis=1).fillna(0).drop(0)
    freq_table.columns = ['intensity', 'Frequency']
    freq_table['Log(Frequency)'] = np.log(freq_table['Frequency']+1)

    fig = px.bar(freq_table, x="intensity", y="Log(Frequency)", template="plotly_white",  width=600, height=400)

    fig.update_traces(marker_color="#696880")
    fig.update_layout(font={"color":"grey", "size":12},
                    title={"text":"FEATURE INTENSITY - FREQUENCY PLOT", 'x':0.5, "font_color":"#3E3D53"})
    
    return fig



def get_missing_values_per_feature_fig(df, cutoff_LOD):
    # check the number of missing values per feature in a histogram
    n_zeros = df.T.apply(lambda x: sum(x<=cutoff_LOD))

    fig = px.histogram(n_zeros, template="plotly_white",  
                    width=600, height=400)

    fig.update_traces(marker_color="#696880")
    fig.update_layout(font={"color":"grey", "size":12, "family":"Sans"},
                    title={"text":"MISSING VALUES PER FEATURE", 'x':0.5, "font_color":"#3E3D53"},
                    xaxis_title="number of missing values", yaxis_title="count", showlegend=False)
    return fig