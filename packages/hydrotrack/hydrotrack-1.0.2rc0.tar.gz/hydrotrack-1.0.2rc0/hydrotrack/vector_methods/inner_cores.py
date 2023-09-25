import pandas as pd
from scipy import stats

def innerc_corretion(current_frame):
    """"  This method get inner cores (INC) into current frame and compute the mean of vectors (distance and direction) of individual clusters in the previous frame. """
    if current_frame[current_frame['threshold_level'] > 0].empty:
        return pd.DataFrame(columns=['dis_inc', 'dir_inc'])
    if len(current_frame) < 1:
        return pd.DataFrame(columns=['dis_inc', 'dir_inc'])
    # Add columns dis_inc and dir_inc in current frame
    current_frame['dis_inc'] = None
    current_frame['dir_inc'] = None
    current_copy = current_frame.copy()
    # Select not nan uids
    current_copy = current_copy[~current_copy['uid'].isnull()]
    # Current frame transform all values into int in uid column
    current_copy['uid'] = current_copy['uid'].astype(int)
    # Groupby uid and threshold_level in current frame
    current_frame_group = current_copy.groupby(['uid'])
    for gidx, cur_group in current_frame_group:
        distance_values = cur_group['dis_'].dropna()
        direction_values = cur_group['dir_'].dropna()
        if len(distance_values) < 2:
            continue
        mean_dis = distance_values.mean()
        mean_dir = stats.circmean(direction_values, high=360, low=0, nan_policy='omit')
        # Sort by threshold lvl
        cur_group = cur_group.sort_values(by=['threshold_level'])        
        # Update current frame with mean values at column dis_mrg and dir_mrg
        current_frame.loc[cur_group.index[0], 'dis_inc'] = mean_dis
        current_frame.loc[cur_group.index[0], 'dir_inc'] = mean_dir
    return current_frame[['dis_inc', 'dir_inc']]