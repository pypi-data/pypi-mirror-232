import glob
import pandas as pd
import pathlib
import multiprocessing as mp
from datetime import datetime, timedelta
from tqdm import tqdm
from hydrotrack.vector_methods import *
from .utils import update_progress, get_columns, read_geodataframe


def vector_methods(name_list, read_function, parallel=True, previous_times=3, merge=True, tempavg=True, icor=True, optflow=True, opt_mtd='lucas-kanade'):
    """ Extract the vector data from the input files. """
    print('Vector methods has been started...')
    # Get features files
    files_list = sorted(glob.glob(name_list['output_path'] + 'features/*.parquet', recursive=True))
    if not files_list:
        print('No files found in the input directory')
        return
    # Check if the first file contains status column when opening
    error_cols = ['timestamp','cluster_id','uid','iuid','threshold_lvl','lifetime','class','dis_','dir_']
    geodf = read_geodataframe(files_list[0], error_columns=error_cols)
    if 'uid' not in geodf.columns:
        print('The first file does not contain uid column, please run the spatial operations first')
        return
    # Extract the timestamp from the path
    tstamp_list = [datetime.strptime(pathlib.Path(x).stem, '%Y%m%d_%H%M') for x in files_list]
    time_delta = timedelta(minutes=name_list['delta_time'])
    boundary_path = name_list['output_path'] + 'features/'
    # Number of cores
    if 'n_jobs' not in name_list.keys():
        name_list['n_jobs'] = mp.cpu_count()
    elif name_list['n_jobs'] == -1:
        name_list['n_jobs'] = mp.cpu_count()
    # Create the progress bar
    pbar = tqdm(total=len(files_list), ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [Elapsed:{elapsed} Remaining:<{remaining}]')
    # Add mehods to the list
    methods_list = []
    if merge:
        methods_list.append('merge')
    if tempavg:
        methods_list.append('tempavg')
    if icor:
        methods_list.append('icor')
    if optflow:
        methods_list.append('optflow')
    if parallel:
        # Pool of workers
        with mp.Pool(name_list['n_jobs']) as pool:
            for _ in pool.imap_unordered(process_timestamp, [(tstamp_list[tstamp], \
                                                        boundary_path, time_delta, \
                                                        previous_times, methods_list, \
                                                        read_function, name_list, opt_mtd) for tstamp in range(len(tstamp_list))]):
                update_progress(1, pbar) # Update the progress bar
        pbar.close()
        pool.close()        
    else:
        for tstamp in range(len(tstamp_list)):
            process_timestamp((tstamp_list[tstamp], boundary_path, time_delta, \
                                previous_times, methods_list, \
                                read_function, name_list, opt_mtd))
            update_progress(1, pbar) # Update the progress bar

def process_timestamp(args):
    
    error_cols = ['timestamp','cluster_id','uid','iuid','threshold_lvl','lifetime','class','dis_','dir_']
    timestamp, boundary_path, time_delta, previous_times, methods_list, read_function, name_list, opt_mtd = args
    current_frame = read_geodataframe(boundary_path + timestamp.strftime('%Y%m%d_%H%M') + '.parquet', error_columns=error_cols)
    previous_stamp = pd.date_range(timestamp - (time_delta * (previous_times - 1)), timestamp - time_delta, freq=time_delta)
    previous_frames = [read_geodataframe(boundary_path + pstamp.strftime('%Y%m%d_%H%M') + '.parquet',error_columns=error_cols) \
                        if pathlib.Path(boundary_path + pstamp.strftime('%Y%m%d_%H%M') + '.parquet').exists() \
                        else pd.DataFrame() for pstamp in previous_stamp]
    # Process the corretions
    for method in methods_list:
        frame = call_corretions((method, current_frame, previous_frames, read_function, name_list, opt_mtd))
        if len(frame) > 0:
            current_frame.loc[frame.index, frame.columns] = frame
    # Save the results
    if not current_frame.empty:
        current_frame.to_parquet(boundary_path + timestamp.strftime('%Y%m%d_%H%M') + '.parquet')
    # Delete the variables
    del current_frame, previous_stamp, previous_frames, frame, \
        timestamp, boundary_path, time_delta, previous_times, methods_list, read_function

def call_corretions(args):
    " Call the corretions methods. "
    method, current_frame, previous_frames, read_function, name_list, opt_mtd = args
    if method == 'merge':
        return merge_corretion(current_frame, previous_frames)
    elif method == 'tempavg':
        return temporal_avg_corretion(current_frame, previous_frames)
    elif method == 'icor':
        innerc_corretion(current_frame)
        return pd.DataFrame(columns=['dis_icor', 'dir_icor'])
    elif method == 'optflow':
        method_frame = optflow_corretion(current_frame,
                                        previous_frames,
                                        read_function,
                                        name_list,
                                        method=opt_mtd)
        return method_frame
    else:
        return pd.DataFrame(columns=['dis_' + method, 'dir_' + method])

if __name__ == '__main__':
    vector_methods(name_list, read_function, parallel=True, previous_times=3, merge=True, tempavg=True, icor=True, optflow=True, opt_mtd='lucas-kanade')