import os
# os.environ['USE_PYGEOS'] = '0'
import numpy as np
import pandas as pd
import geopandas as gpd
import pathlib
import multiprocessing as mp
from rasterio import features
from rasterio import mask
from shapely.geometry import Polygon
from .utils import update_progress, get_filestamp, get_columns, set_operator, set_dbscan, get_input_files, calc_statistic, save_parquet
from tqdm import tqdm


def extract_features(name_list, read_func, save_feat=True):
    '''Return a list of features from a list of names'''
    # Get the input files
    files_list = get_input_files(name_list)
    if len(files_list) < 1:
        print('There are not enough files to process')
        return
    # Set the operator to be used
    operator = set_operator(name_list)
    # Set the DBSCAN parameters
    dbscan = set_dbscan()
    # Number of cores
    if 'n_jobs' not in name_list.keys():
        name_list['n_jobs'] = mp.cpu_count()
    elif name_list['n_jobs'] == -1:
        name_list['n_jobs'] = mp.cpu_count()
    print('Extract features process has been started...')
    # Create the output features directories
    pathlib.Path(name_list['output_path'] + 'features/').mkdir(parents=True, exist_ok=True)
    # Create the progress bar
    pbar = tqdm(total=len(files_list), ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [Elapsed:{elapsed} Remaining:<{remaining}]')
    with mp.Pool(name_list['n_jobs']) as pool:
        for _ in pool.imap_unordered(get_features, [(file, name_list, operator, read_func, dbscan, save_feat) for _, file in enumerate(files_list)]):
            update_progress(1, pbar)
    pbar.close()
    pool.close()

def get_features(args):
    """Return a list of features from a file"""
    # For dBZ Radar data convert to mm/h in calculate statistics
    file, name_list, operator, read_func, dbscan, save_feat = args
    mean_dbz = False
    if 'mean_dbz' in name_list.keys() and name_list['mean_dbz']:
        mean_dbz = True
    # Get the timestamp value
    timestamp_value = get_filestamp(name_list, file)
    # Initialize the features
    features_columns = get_columns()['features'] # Get the features columns
    main_features = pd.DataFrame(columns=features_columns) 
    feature_file = name_list['output_path'] + 'features/{}.parquet'.format(timestamp_value.strftime('%Y%m%d_%H%M'))
    # Read the data from the file using the read_func
    try:
        data = read_func(file)
    except Exception as e:
        print('Error reading file: {}'.format(file), e)
        if save_feat:
            save_parquet(gpd.GeoDataFrame(main_features), feature_file)
        return
    # Segment the data based on the threshold
    x_y = segmentation(data, name_list, operator)
    # Create an empty array based on shape of data with dimensions with len of name_list['thresholds']
    shape = (len(name_list['thresholds']), data.shape[0], data.shape[1])
    cluster_img = np.zeros(shape, dtype=float)
    # Calculate the features for each threshold
    for thld_lvl in range(len(x_y)):
        points = x_y[thld_lvl]
        if len(points) == 0:
            continue
        # Get the cluster labels and features by clustering
        clusters, cluster_dict, cluster_coords = clustering(dbscan, points, data, name_list['min_cluster_size'][thld_lvl])
        # Fill cluster_img with the cluster labels
        cluster_img[thld_lvl, clusters[:, 0], clusters[:, 1]] = clusters[:, -1]
        cluster_features = pd.DataFrame() # Empty dataframe to store the features
        # Calculate statistics for each cluster
        for id_c in cluster_dict.keys():
            stats = calc_statistic(cluster_dict[id_c], mean_dbz)
            stats.columns = stats.columns.str.replace('25%', 'Q1').str.replace('50%', 'Q2').str.replace('75%', 'Q3').str.replace('count', 'size')
            stats['cluster_id'] = id_c
            stats['array_values'] = [cluster_dict[id_c]]
            stats['array_x'] = [cluster_coords[id_c][:, 1]]
            stats['array_y'] = [cluster_coords[id_c][:, 0]]
            cluster_features = pd.concat([cluster_features, stats], axis=0)
        cluster_features['threshold'] = name_list['thresholds'][thld_lvl]
        cluster_features['threshold_level'] = thld_lvl
        # cluster_features['cluster_id'] = np.unique(clusters[:, -1])
        cluster_features['file'] = file
        cluster_features['timestamp'] = timestamp_value
        cluster_features.set_index('cluster_id', inplace=True, drop=True)
        # Rasterize the clusters
        geometries = rasterize(clusters, data.shape)
        # Merge the geometries and cluster features by index
        geometries.sort_index(inplace=True)
        cluster_features.sort_index(inplace=True)
        cluster_features = cluster_features.merge(geometries, left_index=True, right_index=True).reset_index()
        main_features = pd.concat([main_features, cluster_features], axis=0)
    # Check if main_features is empty
    if main_features.empty:
        # Save features to file
        if save_feat:
            save_parquet(gpd.GeoDataFrame(main_features), feature_file)
        return
    # Main features are geodataframe
    main_features = gpd.GeoDataFrame(main_features, geometry='geometry')
    main_features.reset_index(inplace=True, drop=True)
    # Save features to file
    if save_feat:
        save_parquet(main_features, feature_file)
    return

def segmentation(data, name_list, operator):
    y_x = []
    for threshold in name_list['thresholds']:
        y_x.append(np.argwhere(operator(data, threshold)))
    return y_x

def clustering(dbscan, points, data, min_cluster_size):
    '''Return the cluster labels for each point'''
    # Fit the dbscan model
    dbscan.fit(points)
    labels_ = np.concatenate((points, dbscan.labels_[:, np.newaxis]), axis=1)
    # Remove noise
    labels_ = labels_[labels_[:, -1] != -1]
    # Filter by count of points labels
    items, count = np.unique(labels_[:, -1], return_counts=True)
    filter_ids = items[count < min_cluster_size]
    # Remove points with less than min_cluster_size points
    labels_ = labels_[~np.isin(labels_[:, -1], filter_ids)]
    # Increment label to start from 1
    labels_[:, -1] += 1
    # Cluster dictionary
    cluster_dict = {}
    cluster_coords = {}
    # Create a list of features for each cluster
    for item in np.unique(labels_[:, -1]):
        points = labels_[labels_[:, -1] == item][:, :-1]
        cluster_dict[item] = np.array(data[points[:, 0], points[:, 1]])
        cluster_coords[item] = points
    return labels_, cluster_dict, cluster_coords

def rasterize(cluster, shape):
    '''Return a geometries in image'''
    raster = np.zeros(shape, dtype=np.int16)
    raster[cluster[:, 0], cluster[:, 1]] = cluster[:, -1].astype(int)
    mask_array = raster != 0
    bounds = []
    bound_id = []
    geometry = pd.DataFrame()    
    # for geo in features.shapes(raster, mask_array, connectivity=8, transform=(1,0,-0.166,0,1,0.03)): # jaxa affine transform
    for geo in features.shapes(raster, mask_array, connectivity=8, transform=(1,0,0,0,1,0)): # imerg affine transform
        bounds.append(Polygon(geo[0]['coordinates'][0]))
        bound_id.append(int(geo[-1]))
    geometry['cluster_id'] = bound_id
    geometry['geometry'] = bounds
    geometry.set_index('cluster_id', inplace=True, drop=True)
    return geometry

if __name__ == '__main__':
    extract_features(name_list, read_func, save_feat=True)