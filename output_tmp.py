import pandas as pd
import time
import pickle
from os import path
import os
import config
from pathlib import Path


def process_protest(df, year):
    print(f'資料筆數： {len(df)}')
    # service_info = pd.DataFrame(columns=['個案編號', '年度', '類別', '建檔日期'])
    # dict_case_no = {'個案編號': df['CASENO']}
    # dict_year = {'年度': map(lambda x: x.year - 1911, df['CASENO'])}
    # dict_plan_type = {'類別': df['PLAN_TYPE']}
    # dict_date_created = {'建檔日期': df['DATE_CREATED']}
    # dict_ca_01 = {'CA01': []}
    service_info_dict = {'個案編號': df['CASENO'], '年度': map(lambda x: x.year - 1911, df['CASENO']), '類別': df['PLAN_TYPE'],
                         '建檔日期': df['DATE_CREATED'], 'CA01': [''] * len(df)}
    print(service_info_dict)


if __name__ == '__main__':
    start = time.time()
    # dir_name_years = os.listdir(config.data_sample_selected_path)
    # for dir_name_year in dir_name_years:
    #     os.listdir(path.join(config.data_sample_selected_path, dir_name_year))
    for dir_year in Path(config.data_sample_selected_path).iterdir():
        year = dir_year.stem
        for file in dir_year.iterdir():
            if 'pretest' in file.stem and file.suffix == '.pickle':
                with file.open('rb') as handle:
                    pretest_df = pd.DataFrame.from_dict(pickle.load(handle))
                    process_protest(pretest_df, year)
            elif 'posttest' in file.stem and file.suffix == '.pickle':
                with file.open('rb') as handle:
                    posttest_df = pd.DataFrame.from_dict(pickle.load(handle))
    end = time.time()
    print('Elapsed time(sec) for output_tmp: ', end - start)
