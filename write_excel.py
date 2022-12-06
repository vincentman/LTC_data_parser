import pandas as pd
import time
import pickle
from os import path
import os
import config
import sys

if __name__ == '__main__':
    start = time.time()
    if sys.argv[1] == 'all_data':
        data_pickle_path = path.join(config.data_serialized_path, config.data_serialized_pickle_name)
        print('reading data pickle.....', data_pickle_path)
        with open(data_pickle_path, 'rb') as handle:
            data_pickle = pickle.load(handle)
        data_df = pd.DataFrame.from_dict(data_pickle)
        data_df.to_excel(
            path.join(config.data_serialized_path, config.data_serialized_xlsx_name), index=False)
    elif sys.argv[1] == 'all_samples_data':
        data_pickle_path = path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name)
        print('reading data pickle.....', data_pickle_path)
        with open(data_pickle_path, 'rb') as handle:
            data_pickle = pickle.load(handle)
        data_df = pd.DataFrame.from_dict(data_pickle)
        data_df.to_excel(
            path.join(config.data_sample_selected_path, config.data_sample_selected_xlsx_name), index=False)

end = time.time()
print('Elapsed time(sec) for write_excel: ', end - start)
