import plotly.express as px
import plotly.graph_objects as go
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

def get_anova_plot(anova):
    # first plot insignificant features
    fig = px.scatter(x=anova[anova['significant'] == False]['F'].apply(np.log),
                    y=anova[anova['significant'] == False]['p'].apply(lambda x: -np.log(x)),
                    template='plotly_white', width=600, height=600)
    fig.update_traces(marker_color="#696880")

    # plot significant features
    fig.add_scatter(x=anova[anova['significant']]['F'].apply(np.log),
                    y=anova[anova['significant']]['p'].apply(lambda x: -np.log(x)),
                    mode='markers+text',
                    text=anova['metabolite'].iloc[:4],
                    textposition='top left', textfont=dict(color='#ef553b', size=7), name='significant')

    fig.update_layout(font={"color":"grey", "size":12, "family":"Sans"},
                    title={"text":"ANOVA - FEATURE SIGNIFICANCE", 'x':0.5, "font_color":"#3E3D53"},
                    xaxis_title="log(F)", yaxis_title="-log(p)", showlegend=False)
    return fig

def get_tukey_volcano_plot(tukey):
    # create figure
    fig = px.scatter(template='plotly_white')

    # plot insignificant values
    fig.add_trace(go.Scatter(x=tukey[tukey['stats_significant'] == False]['stats_diff'],
                            y=tukey[tukey['stats_significant'] == False]['stats_p'].apply(lambda x: -np.log(x)),
                            mode='markers', marker_color='#696880', name='insignificant'))

    # plot significant values
    fig.add_trace(go.Scatter(x=tukey[tukey['stats_significant']]['stats_diff'],
                            y=tukey[tukey['stats_significant']]['stats_p'].apply(lambda x: -np.log(x)),
                            mode='markers+text', text=tukey['stats_metabolite'].iloc[:4], textposition='top left', 
                            textfont=dict(color='#ef553b', size=8), marker_color='#ef553b', name='significant'))

    fig.update_layout(font={"color":"grey", "size":12, "family":"Sans"},
                    title={"text":"TUKEY - FEATURE DIFFERENCE", 'x':0.5, "font_color":"#3E3D53"},
                    xaxis_title="stats_diff", yaxis_title="-log(p)")
    return fig

def get_metabolite_boxplot(anova, data, metabolite):
    p_value = anova.set_index('metabolite')._get_value(metabolite, "p")
    df = data[['ATTRIBUTE_Time-Point', metabolite]]
    title = f"{metabolite}<br>p-value: {p_value}"
    fig = px.box(df, x='ATTRIBUTE_Time-Point', y=metabolite, template='plotly_white',
                 width=800, height=600, points='all', color='ATTRIBUTE_Time-Point')

    fig.update_layout(font={"color":"grey", "size":12, "family":"Sans"},
                      title={"text":title, 'x':0.5, "font_color":"#3E3D53"},
                      xaxis_title="time point", yaxis_title="intensity scales and centered")
    return fig