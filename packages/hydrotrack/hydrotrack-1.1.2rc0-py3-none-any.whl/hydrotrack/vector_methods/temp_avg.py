from scipy import stats
import pandas as pd
pd.set_option('mode.chained_assignment', None)

def temporal_avg_corretion(current_frame, previous_frames):
    """"  This method get latest previous frames and compute the mean vector into current frame. """
    if len(previous_frames) < 1 or len(previous_frames[-1]) == 0:
        return pd.DataFrame(columns=['dis_avg', 'dir_avg'])
    if len(current_frame) < 1:
        return pd.DataFrame(columns=['dis_avg', 'dir_avg'])
    # Concatenate previous frames into one dataframe if not empty in previous_frames list
    past_frames = pd.concat(previous_frames)
    # Add columns dis_tavg and dir_tavg in current frame
    current_frame['dis_avg'] = None
    current_frame['dir_avg'] = None
    # Groupby uid and threshold_level in current frame
    current_frame_group = current_frame.groupby(['uid', 'threshold_level'])
    for gidx, cur_group in current_frame_group:
        previous_values = past_frames[(past_frames['uid'] == gidx[0]) & (past_frames['threshold_level'] == gidx[1])]
        # Check if prev_values contains dis_ values
        distance_values = previous_values['dis_'].dropna()
        direction_values = previous_values['dir_'].dropna()
        mean_dis = distance_values.mean()
        try:
            mean_dir = stats.circmean(direction_values, high=360, low=0, nan_policy='omit')
        except:
            continue
        # Update current frame with mean values at column dis_mrg and dir_mrg
        current_frame.loc[cur_group.index, 'dis_avg'] = mean_dis
        current_frame.loc[cur_group.index, 'dir_avg'] = mean_dir
    return current_frame[['dis_avg', 'dir_avg']]