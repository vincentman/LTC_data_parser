import config
import pandas as pd
import pickle
import os.path as path
import sys
import time

start = time.time()
if sys.argv[1] == 'post_has_no_pre':
    with open(path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name), 'rb') as handle:
        all_df = pd.DataFrame.from_dict(pickle.load(handle))
    all_df.drop_duplicates(inplace=True)
    posttest_df = all_df[all_df['PLAN_TYPE'] == '複評']
    posttest_df.drop_duplicates(subset=['CASENO'], keep='first', inplace=True)
    post_has_pre_test_df = all_df[all_df['CASENO'].isin(posttest_df['CASENO']) & (all_df['PLAN_TYPE'] == '初評')]
    post_has_pre_test_df.drop_duplicates(subset=['CASENO'], keep='first', inplace=True)
    merged_df = pd.concat([posttest_df, post_has_pre_test_df], axis=0)
    post_has_no_pre_df = merged_df.drop_duplicates(subset=['CASENO'], keep=False)
    post_has_no_pre_df.to_excel(
        path.join(config.data_output_tmp_path, '有複評沒初評.xlsx'), index=False)
end = time.time()
print('Elapsed time(sec) for search: ', end - start)
