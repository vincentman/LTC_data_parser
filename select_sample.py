import pandas as pd
import time
import pickle
from os import path
import os
import config

if __name__ == '__main__':
    start = time.time()
    data_pickle_path = path.join(config.data_serialized_path, config.data_serialized_file_name)
    print('reading data pickle.....', data_pickle_path)
    with open(data_pickle_path, 'rb') as handle:
        data_pickle = pickle.load(handle)
    data_df = pd.DataFrame.from_dict(data_pickle)
    file_name_years = os.listdir(config.sample_select_list_path)
    data_all_years_samples_df = pd.DataFrame()
    for file_name_year in file_name_years:
        sample_list_file_path = path.join(config.sample_select_list_path, file_name_year)
        print('reading sample list..... => ', sample_list_file_path)
        sample_list_df = pd.read_excel(sample_list_file_path, engine='xlrd')  # use xlrd to read .xls file
        sample_list = sample_list_df['案號']
        data_case_no_df = data_df['CASENO'].apply(str)
        data_one_year_samples_df = data_df[data_case_no_df.isin(sample_list)]
        data_all_years_samples_df = pd.concat([data_all_years_samples_df, data_one_year_samples_df], axis=0)
    with open(path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name),
              'wb') as handle:
        pickle.dump(data_all_years_samples_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    data_all_years_samples_df.to_excel(
        path.join(config.data_sample_selected_path,
                  config.data_sample_selected_xlsx_name), index=False)
    end = time.time()
    print('Elapsed time(sec) for select_sample: ', end - start)
