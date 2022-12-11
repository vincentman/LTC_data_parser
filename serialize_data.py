import pandas as pd
import time
import pickle
from os import path
import os
import config
from pathlib import Path

if __name__ == '__main__':
    start = time.time()
    os.makedirs(config.data_serialized_path, exist_ok=True)
    dir_name_years = os.listdir(config.data_path)
    all_years_df = pd.DataFrame()
    for item_in_dir in Path(config.data_path).iterdir():
        if not item_in_dir.is_dir():
            continue
        year_df = pd.DataFrame()
        dir_name_year = item_in_dir.name
        os.makedirs(path.join(config.data_serialized_path, dir_name_year), exist_ok=True)
        for item_in_year_dir in item_in_dir.iterdir():
            if item_in_year_dir.is_dir():
                continue
            print('reading excel..... => ', item_in_year_dir.name)
            month_df = pd.read_excel(item_in_year_dir.absolute(), index_col=None, engine='openpyxl')
            year_df = pd.concat([year_df, month_df], axis=0)
        if not year_df.empty:
            pickle_path = path.join(config.data_serialized_path, dir_name_year, f'{dir_name_year}_serialized.pickle')
            print('writing pickle..... => ', pickle_path)
            with open(pickle_path,
                      'wb') as handle:
                pickle.dump(year_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
        all_years_df = pd.concat([all_years_df, year_df], axis=0)
    pickle_path = path.join(config.data_serialized_path, config.data_serialized_pickle_name)
    with open(pickle_path, 'wb') as handle:
        all_years_df.drop_duplicates(inplace=True)
        print(f'writing pickle(count: {len(all_years_df)})..... => {pickle_path}')
        pickle.dump(all_years_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    end = time.time()
    print('Elapsed time(sec) for serialize_data: ', end - start)
