import pandas as pd
import time
import pickle
from os import path
import os
import config

if __name__ == '__main__':
    start = time.time()
    os.makedirs(config.data_serialize_path, exist_ok=True)
    dir_name_years = os.listdir(config.data_path)
    for dir_name_year in dir_name_years:
        df_year = pd.DataFrame()
        file_name_months = os.listdir(path.join(config.data_path, dir_name_year))
        os.makedirs(path.join(config.data_serialize_path, dir_name_year), exist_ok=True)
        for file_name_month in file_name_months:
            file_path = path.join(config.data_path, dir_name_year, file_name_month)
            print('reading excel..... => ', file_path)
            df_month = pd.read_excel(file_path, index_col=None, engine='openpyxl')
            # print(df.info())
            # print(df.describe())
            df_year = pd.concat([df_year, df_month], axis=0)
        if len(file_name_months):
            pickle_path = path.join(config.data_serialize_path, dir_name_year, f'{dir_name_year}_serialize.pickle')
            print('writing pickle..... => ', pickle_path)
            with open(pickle_path,
                      'wb') as handle:
                pickle.dump(df_year, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open(join(config.data_serialize_path, f'all_serialize.pickle'), 'wb') as handle:
    #     pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    end = time.time()
    print('Elapsed time(sec) for serialize_data: ', end - start)
