import config
import pandas as pd
import pickle
import os.path as path
import sys
import time
from output_tmp import check_if_b_contained_in_a

if __name__ == '__main__':
    start = time.time()
    if sys.argv[1] == 'check_hospital':
        sample_list_file_path = path.join(config.sample_select_list_path_hospital,
                                          config.sample_select_list_file_name_hospital)
        sample_list_df = pd.read_excel(sample_list_file_path, engine='xlrd')  # use xlrd to read .xls file
        print(f'reading sample list for hospital(count: {len(sample_list_df)})..... => {sample_list_file_path}')
        sample_caseno_list = sample_list_df['案號']
        with open(path.join(config.data_sample_selected_path, config.data_selected_pickle_name_hospital),
                  'rb') as handle:
            data_df = pd.DataFrame.from_dict(pickle.load(handle))
        data_df.drop_duplicates(subset=['CASENO'], keep='first', inplace=True)  # 筆
        data_caseno_list = data_df['CASENO']
        print(f'取得資料筆數(去掉重覆CASENO)： {len(data_df)}')
        loss_caseno_list = check_if_b_contained_in_a(data_caseno_list, sample_caseno_list)
        print(f'未找到資料的案號_屏基: {len(loss_caseno_list)}筆')
        if len(loss_caseno_list) > 0:
            with pd.ExcelWriter(path.join(config.data_sample_selected, '未找到資料的案號_屏基.xlsx'),
                                engine='openpyxl') as writer:
                loss_caseno_list.to_excel(writer, sheet_name="遺失案號", index=False)
    end = time.time()
    print('Elapsed time(sec) for search: ', end - start)
