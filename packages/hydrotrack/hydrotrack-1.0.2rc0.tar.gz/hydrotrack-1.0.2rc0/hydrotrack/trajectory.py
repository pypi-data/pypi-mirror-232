import glob
import geopandas as gpd
import pathlib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from shapely.ops import linemerge
from shapely.wkt import loads
from shapely.geometry import MultiLineString
from tqdm import tqdm
from .utils import update_progress, get_columns, find_previous_frame, save_parquet


def trajectory_linking(name_list):
    """ Link trajectories together.
    """
    print('Trajectory linking has been started (Serial mode) ...')
    # Get features files
    files_list = sorted(glob.glob(name_list['output_path'] + 'features/*.parquet', recursive=True))
    if not files_list:
        print('No files found in the input directory')
        return
    tstamp_list = [datetime.strptime(pathlib.Path(x).stem, '%Y%m%d_%H%M') for x in files_list]
    dt_time = timedelta(minutes=name_list['delta_time'])
    features_path = name_list['output_path'] + 'features/'
    # Create the progress bar
    pbar = tqdm(total=len(files_list), ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [Elapsed:{elapsed} Remaining:<{remaining}]')
    # Set initial UID
    uid = 1
    counter = 0
    # Loop through the files
    for cstamp in range(len(tstamp_list)):
        current_timestamp = tstamp_list[cstamp]
        current_path = features_path + current_timestamp.strftime('%Y%m%d_%H%M') + '.parquet'
        current_frame = gpd.read_parquet(current_path) # Read the current frame
        current_frame.loc[:, get_columns()['trajectory']] = np.nan
        if current_frame.empty:
            update_progress(1, pbar)
            save_parquet(current_frame, current_path) # Save the current frame
            continue
        if counter == 0:
            current_frame = new_frame(current_frame, uid, dt_time)
            current_frame = refact_inside_uids(current_frame, dt_time)
            if ~np.isnan(current_frame['uid'].max()):
                uid = current_frame['uid'].max() + 1
            else:
                uid = uid + 1
            counter += 1
            save_parquet(current_frame, current_path) # Save the current frame
            update_progress(1, pbar)
            continue
        # Previous frame
        previous_stamp = current_timestamp - dt_time
        previous_file = features_path + previous_stamp.strftime('%Y%m%d_%H%M') + '.parquet'
        if pathlib.Path(previous_file).exists():
            previous_frame = gpd.read_parquet(previous_file) # Read the previous frame
        else:
            previous_frame, previous_stamp, dt_time = find_previous_frame(current_timestamp,
                                                                          cstamp,
                                                                          tstamp_list,
                                                                          files_list,
                                                                          name_list,
                                                                          dt_time,
                                                                          error_columns=get_columns()['features'] + \
                                                                                        get_columns()['spatial'] + \
                                                                                        get_columns()['trajectory'])
        # Check if previous frame is empty
        if previous_frame is None:
            current_frame = new_frame(current_frame, uid, dt_time)
            current_frame = refact_inside_uids(current_frame, dt_time)
            if ~np.isnan(current_frame['uid'].max()):
                uid = current_frame['uid'].max() + 1
            else:
                uid = uid + 1
            counter += 1
            save_parquet(current_frame, current_path) # Save the current frame
            update_progress(1, pbar)
            continue
        # Get previous index in current frame
        not_none_current = current_frame.loc[(~current_frame['prev_idx'].isnull()) &
                                             (current_frame['prev_idx']!= -1)]
        if not_none_current.empty: # All clusters are new
            current_frame = new_frame(current_frame, uid, dt_time)
            current_frame = refact_inside_uids(current_frame, dt_time)
            if np.isnan(current_frame['uid'].max()):
                uid_list = np.arange(uid, uid + len(current_frame), 1, dtype=int)
                iuids = [float(str(uid_list[x]) + '.' + str(x)) for x in range(len(uid_list))]
                current_frame['uid'] = uid_list
                current_frame['iuid'] = iuids
                current_frame['lifetime'] = dt_time
            if ~np.isnan(current_frame['uid'].max()):
                uid = current_frame['uid'].max() + 1
            else:
                uid = uid + 1
            counter += 1
            save_parquet(current_frame, current_path) # Save the current frame
            update_progress(1, pbar)
            continue
        # Get uid from previous frame
        not_none_current = not_none_current['prev_idx'].apply(lambda x: previous_frame.loc[x])
        current_frame.loc[not_none_current.index, 'uid'] = not_none_current['uid']
        current_frame.loc[not_none_current.index, 'iuid'] = not_none_current['iuid']
        delta_life = current_timestamp - previous_stamp
        current_frame.loc[not_none_current.index, 'lifetime'] = not_none_current['lifetime'] + delta_life
        # Merge trajectories
        current_frame['trajectory'] = loads(current_frame['trajectory'])
        previous_frame['trajectory'] = loads(previous_frame['trajectory'])
        # Merge the trajectorie
        trajectory = current_frame.loc[not_none_current.index].apply(lambda x: new_trajectory(x['trajectory'],
                                                                    previous_frame.loc[x['prev_idx']]['trajectory']) \
                                                                    if previous_frame.loc[x['prev_idx']]['trajectory'].is_empty == False \
                                                                    else x['trajectory'], axis=1)
        current_frame.loc[not_none_current.index, 'trajectory'] = trajectory # Update the trajectory
        current_frame['trajectory'] = current_frame['trajectory'].astype(str) # Convert to string
        # Add news
        none_current = current_frame[current_frame['prev_idx'].isnull()].index
        if len(none_current) > 0:
            none_current = new_frame(current_frame.loc[none_current], uid, dt_time)
            current_frame.loc[none_current.index, none_current.columns] = none_current
            current_frame = refact_inside_uids(current_frame, dt_time)
        if ~np.isnan(current_frame['uid'].max()):
            uid = current_frame['uid'].max() + 1
        else:
            uid = uid + 1
        counter += 1
        # Check duplicates at uid column and get index
        dup_idx = check_dup(current_frame)
        uid_lust = np.arange(uid, uid + len(dup_idx), 1, dtype=int)
        current_frame.loc[dup_idx, 'uid'] = uid_lust
        current_frame = refact_inside_uids(current_frame, dt_time)
        save_parquet(current_frame, current_path) # Save the current frame
        update_progress(1, pbar) # Update the progress bar
    pbar.close()

def new_frame(frame, max_uid, time_delta):
    # lock the threshold level 0
    new_index = frame.loc[(frame['uid'].isnull()) & (frame['threshold_level'] == 0)].index.values
    if len(new_index) == 0:
        return frame
    # Create new uid
    uid_list = np.arange(max_uid, max_uid + len(new_index), 1, dtype=int)
    frame.loc[new_index, 'uid'] = uid_list
    frame.loc[new_index, 'lifetime'] = time_delta
    return frame

def check_dup(df):
    dup_lvl = df[df['threshold_level'] == 0]
    dup_idx = dup_lvl[dup_lvl.duplicated(subset=['uid'], keep=False)].index
    dup_idx = df.loc[dup_idx].groupby('uid')['size'].idxmin()
    return dup_idx

def refact_inside_uids(frame, delta_time):
    # Get the inside index
    insd_inx = frame[(~frame['inside_idx'].isnull())]
    # Lock inside index threshold level 0
    insd_idx_lv0 = insd_inx[insd_inx['threshold_level'] == 0]
    insd_idx_idx = insd_idx_lv0.index
    insd_idx_val = insd_idx_lv0['inside_idx'].values
    # # Create column iuid if not exist
    # if 'iuid' not in frame.columns:
    #     frame['iuid'] = np.nan
    for idx, val in zip(insd_idx_idx, insd_idx_val):
        uid_vl = str(int(frame.loc[idx]['uid']))
        inside_counter = 999
        for v in val:
            thld_vl = frame.loc[v]['threshold_level']
            if np.isnan(frame.loc[v,'iuid']):
                frame.loc[v,'uid'] = int(uid_vl) # Add the uid to the inside index
                frame.loc[v,'iuid'] = float(uid_vl +'.'+'0' * (thld_vl - 1) + str(inside_counter))
                frame.loc[v,'lifetime'] = delta_time
                inside_counter -= 1
            else:
                frame.loc[v,'uid'] = int(uid_vl)
    # Get touching_idx index
    tch_idx = frame[(~frame['touching_idx'].isnull())].index
    tch_idx_idx = frame.loc[tch_idx]['touching_idx'].values
    thd_uids = frame.loc[tch_idx_idx][['uid','iuid']].values
    # Add the uid and iuid to the touching_idx
    frame.loc[tch_idx, ['uid','iuid']] = thd_uids
    return frame

def new_trajectory(current_line, previous_line):
    try: # TODO: Check the type of current and previous line to avoid error
        # Check if previous line is multiline
        if previous_line.type == 'MultiLineString':
            previous_line = [line for line in previous_line.geoms]
            previous_line.insert(0, current_line)
            merged = MultiLineString(previous_line)
        elif current_line.type == 'MultiLineString':
            current_line = [line for line in current_line.geoms]
            current_line.append(previous_line)
            merged = MultiLineString(current_line)
        else:
            merged = linemerge([current_line, previous_line])
        return merged
    except:
        return current_line
    
if __name__ == '__main__':
    trajectory_linking(name_list)