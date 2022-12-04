import pandas as pd
import time
import pickle
from os import path
import os
import config

if __name__ == '__main__':
    start = time.time()
    os.makedirs(config.data_serialized_path, exist_ok=True)
    dir_name_years = os.listdir(config.data_path)
    all_years_df = pd.DataFrame()
    for dir_name_year in dir_name_years:
        year_df = pd.DataFrame()
        file_name_months = os.listdir(path.join(config.data_path, dir_name_year))
        os.makedirs(path.join(config.data_serialized_path, dir_name_year), exist_ok=True)
        for file_name_month in file_name_months:
            file_path = path.join(config.data_path, dir_name_year, file_name_month)
            print('reading excel..... => ', file_path)
            month_df = pd.read_excel(file_path, index_col=None, engine='openpyxl')
            # print(df.info())
            # print(df.describe())
            year_df = pd.concat([year_df, month_df], axis=0)
        if len(file_name_months):
            pickle_path = path.join(config.data_serialized_path, dir_name_year, f'{dir_name_year}_serialized.pickle')
            print('writing pickle..... => ', pickle_path)
            with open(pickle_path,
                      'wb') as handle:
                pickle.dump(year_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
        all_years_df = pd.concat([all_years_df, year_df], axis=0)
    pickle_path = path.join(config.data_serialized_path, config.data_serialized_file_name)
    with open(pickle_path, 'wb') as handle:
        print('writing pickle..... => ', pickle_path)
        pickle.dump(all_years_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    end = time.time()
    print('Elapsed time(sec) for serialize_data: ', end - start)
