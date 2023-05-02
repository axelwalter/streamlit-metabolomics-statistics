import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pingouin as pg
import skbio # Don't import on Windows!!
from scipy.spatial import distance
from scipy.cluster.hierarchy import dendrogram, linkage

def clean_up_md(md):
    md = md.copy() #storing the files under different names to preserve the original files
    # remove the (front & tail) spaces, if any present, from the rownames of md
    md.index = [name.strip() for name in md.index]
    # for each col in md
    # 1) removing the spaces (if any)
    # 2) replace the spaces (in the middle) to underscore
    # 3) converting them all to UPPERCASE
    for col in md.columns:
        if md[col].dtype == str:
            md[col] = [item.strip().replace(" ", "_").upper() for item in md[col]]
    return md

def clean_up_ft(ft):
    ft = ft.copy() #storing the files under different names to preserve the original files
    # drop all columns that are not mzML or mzXML file names
    ft.drop(columns=[col for col in ft.columns if ".mzML" not in col], inplace=True)
    # remove " Peak area" from column names, contained after mzmine pre-processing
    ft.rename(columns={col: col.replace(" Peak area", "").strip() for col in ft.columns}, inplace=True)
    return ft

def check_columns(md, ft):
    if sorted(ft.columns) == sorted(md.index):
            st.success(f"All {len(ft.columns)} files are present in both meta data & feature table.")
    else:
        st.warning("Not all files are present in both meta data & feature table.")
        # print the md rows / ft column which are not in ft columns / md rows and remove them
        ft_cols_not_in_md = [col for col in ft.columns if col not in md.index]
        st.warning(f"These {len(ft_cols_not_in_md)} columns of feature table are not present in metadata table and will be removed:\n{', '.join(ft_cols_not_in_md)}")
        ft.drop(columns=ft_cols_not_in_md, inplace=True)
        md_rows_not_in_ft = [row for row in md.index if row not in ft.columns]
        st.warning(f"These {len(md_rows_not_in_ft)} rows of metadata table are not present in feature table and will be removed:\n{', '.join(md_rows_not_in_ft)}")
        md.drop(md_rows_not_in_ft, inplace=True)
    return md, ft

def remove_blank_features(blanks, samples, cutoff):
    # Getting mean for every feature in blank and Samples
    avg_blank = blanks.mean(axis=1, skipna=False) # set skipna = False do not exclude NA/null values when computing the result.
    avg_samples = samples.mean(axis=1, skipna=False)

    # Getting the ratio of blank vs samples
    ratio_blank_samples = (avg_blank+1)/(avg_samples+1)

    # Create an array with boolean values: True (is a real feature, ratio<cutoff) / False (is a blank, background, noise feature, ratio>cutoff)
    is_real_feature = (ratio_blank_samples<cutoff)

    # Checking if there are any NA values present. Having NA values in the 4 variables will affect the final dataset to be created
    # temp_NA_Count = pd.concat([avg_blank, avg_samples, ratio_blank_samples, is_real_feature], 
    #                         keys=['avg_blank', 'avg_samples', 'ratio_blank_samples', 'bg_bin'], axis = 1)
    
    # print('No. of NA values in the following columns: ')
    # na_count_df = pd.DataFrame(temp_NA_Count.isna().sum(), columns=['NA'])

    # Calculating the number of background features and features present (sum(bg_bin) equals number of features to be removed)
    n_background = len(samples)-sum(is_real_feature)
    n_real_features = sum(is_real_feature)

    blank_removal = samples[is_real_feature.values]

    return blank_removal, n_background, n_real_features

def get_cutoff_LOD(df):
    # get the minimal value that is not zero (lowest measured intensity)
    return round(df.replace(0, np.nan).min(numeric_only=True).min())

def impute_missing_values(df, cutoff_LOD):
    # impute missing values (0) with a random value between zero and lowest intensity (cutoff_LOD)
    return df.apply(lambda x: [np.random.randint(0, cutoff_LOD) if v == 0 else v for v in x])

def normalize_column_wise(df):
    # normalize values column-wise (sample centric)
    return df.apply(lambda x: x/np.sum(x), axis=0)

def transpose_and_scale(feature_df, meta_data_df, cutoff_LOD):
    # remove meta data rows that are not samples
    md_rows_not_in_samples = [row for row in meta_data_df.index if row not in feature_df.index]
    md_samples = meta_data_df.drop(md_rows_not_in_samples)

    # put the rows in the feature table and metadata in the same order
    feature_df.sort_index(inplace=True)
    md_samples.sort_index(inplace=True)

    try:
        if not list(set(md_samples.index == feature_df.index))[0] == True:
            st.warning("Sample names in feature and metadata table are NOT the same!")
    except:
        st.warning("Sample names in feature and metadata table can NOT be compared. Please check your tables!")

    n_zeros = feature_df.apply(lambda x: sum(x<=cutoff_LOD))

    c1, c2 = st.columns(2)
    c1.metric(f"Total missing values in dataset (coded as <= {cutoff_LOD})", str(round(((feature_df<=cutoff_LOD).to_numpy()).mean(), 3)*100)+" %")
    c2.metric(f"\nMetabolites with measurements in at least 50 % of the samples", str(round((((n_zeros/feature_df.shape[0])<=0.5).mean()*100), 2))+" %")

    # Deselect metabolites with more than 50 % missing values. This helps to get rid of features that are present in too few samples to conduct proper statistical tests
    feature_df = feature_df[feature_df.columns[(n_zeros/feature_df.shape[0])<0.5]]
    
    scaled = pd.DataFrame(StandardScaler().fit_transform(feature_df), index=feature_df.index, columns=feature_df.columns)
    data = pd.merge(md_samples, scaled, left_index=True, right_index=True, how="inner")
    # scale and return
    return scaled, data 

def gen_anova_data(df, columns, groups_col):
    for col in columns:
        result = pg.anova(data=df, dv=col, between=groups_col, detailed=True).set_index('Source')
        p = result.loc[groups_col, 'p-unc']
        f = result.loc[groups_col, 'F']
        yield col, p, f

def add_bonferroni_to_anova(anova):
    # add Bonferroni corrected p-values for multiple testing correction
    if 'p-corrected' not in anova.columns:
        anova.insert(2, 'p-corrected', pg.multicomp(anova['p'], method='bonf')[1])
    # add significance
    if 'significant' not in anova.columns:
        anova.insert(3, 'significant', anova['p-corrected'] < 0.05)
    # sort by p-value
    anova.sort_values('p', inplace=True)
    return anova

def gen_pairwise_tukey(df, elements, metabolites, attribute):
    """ Yield results for pairwise Tukey test for all metabolites between start and end time points."""
    for metabolite in metabolites:
        df_for_tukey = df.iloc[np.where(df[attribute].isin(elements))][[metabolite, attribute]]
        tukey = pg.pairwise_tukey(df_for_tukey, dv=metabolite, between=attribute)
        yield metabolite, tukey['diff'], tukey['p-tukey']

def add_bonferroni_to_tukeys(tukey):
    if 'stats_p-corrected' not in tukey.columns:
        # add Bonferroni corrected p-values
        tukey.insert(3, 'stats_p-corrected', pg.multicomp(tukey['stats_p'], method='bonf')[1])
        # add significance
        tukey.insert(4, 'stats_significant', tukey['stats_p-corrected'] < 0.05)
        # sort by p-value
        tukey.sort_values('stats_p', inplace=True)
    return tukey

def get_pca_df(scaled, n=5):
    #calculating Principal components
    pca = PCA(n_components=n)
    pca_df = pd.DataFrame(data = pca.fit_transform(scaled), columns = [f'PC{x}' for x in range(1, n+1)])
    pca_df.index = scaled.index
    return pca, pca_df

def permanova_pcoa(scaled, distance_matrix, attribute):
    # Create the distance matrix from the original data
    distance_matrix = skbio.stats.distance.DistanceMatrix(distance.squareform(distance.pdist(scaled.values, distance_matrix)))
    # perform PERMANOVA test
    permanova = skbio.stats.distance.permanova(distance_matrix, attribute)
    permanova['R2'] = 1 - 1 / (1 + permanova['test statistic'] * permanova['number of groups'] / (permanova['sample size'] - permanova['number of groups'] - 1))
    # perfom PCoA
    pcoa = skbio.stats.ordination.pcoa(distance_matrix)

    return permanova, pcoa

def order_df_for_heatmap(scaled):
    # SORT DATA TO CREATE HEATMAP

    # Compute linkage matrix from distances for hierarchical clustering
    linkage_data_ft = linkage(scaled, method='complete', metric='euclidean')
    linkage_data_samples = linkage(scaled.T, method='complete', metric='euclidean')

    # Create a dictionary of data structures computed to render the dendrogram. 
    # We will use dict['leaves']
    cluster_samples = dendrogram(linkage_data_ft, no_plot=True)
    cluster_ft = dendrogram(linkage_data_samples, no_plot=True)

    # Create dataframe with sorted samples
    ord_samp = scaled.copy()
    ord_samp.reset_index(inplace=True)
    ord_samp = ord_samp.reindex(cluster_samples['leaves'])
    ord_samp.rename(columns={'index': 'Filename'}, inplace=True)
    ord_samp.set_index('Filename', inplace=True)

    # Create dataframe with sorted features
    ord_ft = ord_samp.T.reset_index()
    ord_ft = ord_ft.reindex(cluster_ft['leaves'])
    ord_ft.rename(columns={'index': 'metabolite'}, inplace=True)
    ord_ft.set_index('metabolite', inplace=True)
    return ord_ft