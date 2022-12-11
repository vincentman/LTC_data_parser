import pandas as pd
import time
import pickle
from os import path
import os
import config

if __name__ == '__main__':
    start = time.time()
    data_pickle_path = path.join(config.data_serialized_path, config.data_serialized_pickle_name)
    print('reading data pickle.....', data_pickle_path)
    with open(data_pickle_path, 'rb') as handle:
        data_pickle = pickle.load(handle)
    data_df = pd.DataFrame.from_dict(data_pickle)
    data_df.drop_duplicates(inplace=True)
    data_df['CASENO'] = data_df['CASENO'].apply(str)
    file_name_years = os.listdir(config.sample_select_list_path)
    all_sample_list_df = pd.DataFrame()
    for file_name_year in file_name_years:
        sample_list_file_path = path.join(config.sample_select_list_path, file_name_year)
        print('reading sample list..... => ', sample_list_file_path)
        sample_list_df = pd.read_excel(sample_list_file_path, engine='xlrd')  # use xlrd to read .xls file
        all_sample_list_df = pd.concat([all_sample_list_df, sample_list_df], axis=0)
    os.makedirs(config.sample_list_serialized_path, exist_ok=True)
    with open(path.join(config.sample_list_serialized_path, config.sample_list_pickle_name), 'wb') as handle:
        all_sample_list_df.drop_duplicates()
        pickle.dump(all_sample_list_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    all_sample_list_df['案號'] = all_sample_list_df['案號'].apply(str)
    all_sample_list_df.drop_duplicates(subset=['案號'], keep='first', inplace=True)
    data_all_years_samples_df = data_df[data_df['CASENO'].isin(all_sample_list_df['案號'])]
    output_excel_path = path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name)
    with open(output_excel_path,
              'wb') as handle:
        print(f'write pickle(count: {len(data_all_years_samples_df)}.....{output_excel_path}')
        pickle.dump(data_all_years_samples_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    end = time.time()
    print('Elapsed time(sec) for select_sample: ', end - start)
