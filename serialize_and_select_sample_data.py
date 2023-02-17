import pandas as pd
import time
import pickle
from os import path
import os
import config
from pathlib import Path
from pandas_ods_reader import read_ods
import argparse
from datetime import datetime
from pathlib import Path

set_is_select_by_caseno = True
set_is_select_the_newest = True  # 只選最新的審核


def get_sample_list_df(is_hospital):
    if is_hospital:
        sample_list_file_path = path.join(config.sample_select_list_path_hospital,
                                          config.sample_select_list_file_name_hospital)
        print('reading sample list for hospital..... => ', sample_list_file_path)
        sample_list_df = pd.read_excel(sample_list_file_path, engine='xlrd')  # use xlrd to read .xls file
    else:
        # with open(path.join(config.sample_list_serialized_path, config.sample_list_pickle_name), 'rb') as handle:
        #     sample_list_df = pd.DataFrame.from_dict(pickle.load(handle))
        sample_list_file_path = path.join(config.sample_select_list_path,
                                          config.final_caseno_list_file_name)
        print('reading sample list..... => ', sample_list_file_path)
        sample_list_df = pd.read_excel(sample_list_file_path, index_col=None, engine='openpyxl')
    sample_list_df.drop_duplicates(subset=['案號'], keep='first', inplace=True)
    print(f'所有年度個案筆數： {len(sample_list_df)}')
    return sample_list_df


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def convert_caseno(x):
    if type(x) == float:
        return str(int(x))
    return str(x)


def select_the_newest(df):
    df_sorted = df.sort_values(['CASENO', 'DATE_CREATED'])
    df_filtered = df_sorted.drop_duplicates(subset=['CASENO'], keep='last')
    return df_filtered


def get_output_pickle_path_for_each_year(is_hospital):
    if is_hospital:
        pickle_path = path.join(config.data_serialized_path, dir_name_year,
                                f'{dir_name_year}_serialized_hospital.pickle')
    else:
        pickle_path = path.join(config.data_serialized_path, dir_name_year,
                                f'{dir_name_year}_serialized.pickle')
    return pickle_path


def get_output_pickle_path_for_all_years(is_hospital):
    if is_hospital:
        pickle_path = path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name_hospital)
    else:
        pickle_path = path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name)
    return pickle_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--hospital", help="For hosptal", type=str2bool, default='False')
    args = parser.parse_args()
    start = time.time()
    os.makedirs(config.data_serialized_path, exist_ok=True)
    if set_is_select_by_caseno:
        all_sample_list_df = get_sample_list_df(args.hospital)
    if args.hospital:
        data_path = Path(config.data_path_hospital)
    else:
        data_path = Path(config.data_path)
    print('read data path: ', data_path)
    all_years_df = pd.DataFrame()
    for item_in_dir in data_path.iterdir():
        if not item_in_dir.is_dir():
            continue
        year_df = pd.DataFrame()
        dir_name_year = item_in_dir.name
        os.makedirs(path.join(config.data_serialized_path, dir_name_year), exist_ok=True)
        for item_in_year_dir in item_in_dir.iterdir():
            if item_in_year_dir.is_dir():
                continue
            # print('reading excel..... => ', item_in_year_dir.name)
            # month_df = pd.read_excel(item_in_year_dir.absolute(), index_col=None, engine='openpyxl')
            print('reading ods..... => ', item_in_year_dir.name)
            month_df = read_ods(item_in_year_dir.absolute())
            month_df['CASENO'] = month_df['CASENO'].apply(convert_caseno)
            if set_is_select_by_caseno:
                month_df = month_df[month_df['CASENO'].isin(all_sample_list_df['案號'])]  # 每月選取符合的案號
            year_df = pd.concat([year_df, month_df], axis=0)
        if not year_df.empty:
            pickle_path = get_output_pickle_path_for_each_year(args.hospital)
            print('writing pickle..... => ', pickle_path)
            with open(pickle_path,
                      'wb') as handle:
                pickle.dump(year_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
        all_years_df = pd.concat([all_years_df, year_df], axis=0)
    all_years_df.drop_duplicates(inplace=True)
    if set_is_select_by_caseno:
        pickle_path = get_output_pickle_path_for_all_years(args.hospital)
    else:
        pickle_path = path.join(config.data_serialized_path, config.data_serialized_pickle_name)
    with open(pickle_path, 'wb') as handle:
        print(f'writing pickle(count: {len(all_years_df)})..... => {pickle_path}')
        pickle.dump(all_years_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    if args.hospital and set_is_select_the_newest:
        all_years_df = select_the_newest(all_years_df)
        pickle_path = path.join(config.data_sample_selected_path,
                                config.data_sample_selected_pickle_name_hospital_newest)
        with open(pickle_path, 'wb') as handle:
            print(f'writing pickle(count: {len(all_years_df)})..... => {pickle_path}')
            pickle.dump(all_years_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    end = time.time()
    print('Elapsed time(sec) for serialize_data: ', end - start)
    print(f'now datetime: {datetime.now().strftime("%Y/%m/%d %H:%M")}')
