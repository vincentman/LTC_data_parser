import pandas as pd
import time
import pickle
from os import path
import os
import config

if __name__ == '__main__':
    start = time.time()
    file_name_years = os.listdir(config.sample_select_list_path)
    for file_name_year in file_name_years:
        # load serialize data pickle to df
        year = file_name_year[0:3]
        data_path_year = path.join(config.data_serialize_path, year, f'{year}_serialize.pickle')
        if not path.exists(data_path_year):
            # raise Exception(f'pickle not exist: {data_path_year}')
            print(f'pickle not exist: {data_path_year}')
        else:
            print('reading pickle..... => ', data_path_year)
            with open(data_path_year, 'rb') as handle:
                data_pickle = pickle.load(handle)
            data_df = pd.DataFrame.from_dict(data_pickle)
            # load sample list
            sample_list_file_path = path.join(config.sample_select_list_path, file_name_year)
            print('reading sample list..... => ', sample_list_file_path)
            sample_list_df = pd.read_excel(sample_list_file_path, engine='xlrd')  # use xlrd to read .xls file
            sample_list = sample_list_df['案號']
            sample_df = data_df[data_df['CASENO'].isin(sample_list)]
            sample_pretest_df = sample_df[sample_df['PLAN_TYPE'] == '初評']
            sample_posttest_df = sample_df[sample_df['PLAN_TYPE'] == '複評']
            os.makedirs(path.join(config.data_sample_selected_path, year), exist_ok=True)
            sample_data_pickle_pretest_path = path.join(config.data_sample_selected_path, year,
                                                        f'{year}{config.sample_pretest_file_postfix}.pickle')
            print('writing pickle with sample list(pretest..... => ', sample_data_pickle_pretest_path)
            with open(sample_data_pickle_pretest_path,
                      'wb') as handle:
                pickle.dump(sample_pretest_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
                sample_pretest_df.to_excel(
                    path.join(config.data_sample_selected_path, year,
                              f'{year}{config.sample_pretest_file_postfix}.xlsx'), index=False)
            sample_data_pickle_posttest_path = path.join(config.data_sample_selected_path, year,
                                                         f'{year}{config.sample_posttest_file_postfix}.pickle')
            print('writing pickle with sample list(posttest..... => ', sample_data_pickle_posttest_path)
            with open(sample_data_pickle_posttest_path,
                      'wb') as handle:
                pickle.dump(sample_posttest_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
                sample_posttest_df.to_excel(
                    path.join(config.data_sample_selected_path, year,
                              f'{year}{config.sample_posttest_file_postfix}.xlsx'), index=False)
    end = time.time()
    print('Elapsed time(sec) for select_sample: ', end - start)
