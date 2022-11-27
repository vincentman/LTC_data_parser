import pandas as pd
import time
import pickle
from os import path
import os
import config
from pathlib import Path
import re
import numpy as np

str_na = 'N/A'
convert_yes_no = (lambda x: str_na if x == str_na else (1 if '是' in x else 0))
convert_digit = (lambda x: str_na if x == str_na else (int(x.split('.')[0])))
convert_digit_nan_0 = (lambda x: 0 if x == str_na else (int(x.split('.')[0])))
disease_item_num = 24


def convert_welfare(income):
    if income[0] == '是':
        return int(1)
    if income[1] == '是':
        return int(2)
    if income[2] == '是':
        return int(3)
    if income[3] == '是':
        return int(4)


def get_converted_diseases_dict(df):
    diseases_dict = {}
    for i in range(24):
        key = f'G4E_CH{i + 1}'
        disease_df = df[key].replace({'1.是': 1, '2.否': 0})
        diseases_dict[key] = disease_df
    return diseases_dict


def get_disease_items_dict(case_no, converted_year, df):
    disease_items_dict = {'個案編號': case_no, '年度': converted_year, '1高血壓': map(convert_yes_no, df['G4E_CH1']),
                          '2糖尿病': map(convert_yes_no, df['G4E_CH2']),
                          '3骨骼系統': map(convert_yes_no, df['G4E_CH3']),
                          '4視覺疾病': map(convert_yes_no, df['G4E_CH4']),
                          '5中風': map(convert_yes_no, df['G4E_CH5']), '6冠狀動脈': map(convert_yes_no, df['G4E_CH6']),
                          '7心房節律': map(convert_yes_no, df['G4E_CH7']),
                          '8癌症': map(convert_yes_no, df['G4E_CH8']), '9呼吸系統': map(convert_yes_no, df['G4E_CH9']),
                          '10消化系統': map(convert_yes_no, df['G4E_CH10']),
                          '11泌尿生殖': map(convert_yes_no, df['G4E_CH11']),
                          '12失智': map(convert_yes_no, df['G4E_CH12']),
                          '13精神疾病': map(convert_yes_no, df['G4E_CH13']),
                          '14自閉症': map(convert_yes_no, df['G4E_CH14']),
                          '15智能不足': map(convert_yes_no, df['G4E_CH15']),
                          '16腦麻': map(convert_yes_no, df['G4E_CH16']),
                          '17帕金森': map(convert_yes_no, df['G4E_CH17']),
                          '18脊損': map(convert_yes_no, df['G4E_CH18']),
                          '19運動神經元': map(convert_yes_no, df['G4E_CH19']),
                          '20傳染疾病': map(convert_yes_no, df['G4E_CH20']),
                          '21感染疾病': map(convert_yes_no, df['G4E_CH21']),
                          '22罕病': map(convert_yes_no, df['G4E_CH22']), '23癲癇': map(convert_yes_no, df['G4E_CH23']),
                          '24其他': map(convert_yes_no, df['G4E_CH24'])}
    return disease_items_dict


def get_diseases_num(diseases_dict, data_length):
    blank = [0] * data_length
    diseases_num_df = pd.DataFrame(blank, columns=['diseases_sum'])
    for i in range(disease_item_num):
        diseases_num_df['diseases_sum'] = np.squeeze(diseases_num_df.values) + diseases_dict[f'G4E_CH{i + 1}'].values
    return diseases_num_df['diseases_sum'].tolist()


def get_response_score(responses_df):
    score2 = list(map(convert_digit_nan_0, responses_df['D_RESP2']))
    score3 = list(map(convert_digit_nan_0, responses_df['D_RESP3']))
    score4 = list(map(convert_digit_nan_0, responses_df['D_RESP4']))
    convert_response_score = (lambda x: 1 if x == 1 else 0)
    converted_score2 = list(map(convert_response_score, score2))
    converted_score3 = list(map(convert_response_score, score3))
    converted_score4 = list(map(convert_response_score, score4))
    return np.sum([np.array(converted_score2), np.array(converted_score3), np.array(converted_score4)], axis=0)


def process_pretest(output_path, df, year):
    df.fillna(str_na, inplace=True)
    blank = [''] * len(df)
    print(f'資料筆數： {len(df)}')
    case_no = df['CASENO']
    converted_year = list(map(lambda x: x.year - 1911, df['DATE_CREATED']))
    service_info_dict = {'個案編號': case_no, '年度': converted_year,
                         '類別': df['PLAN_TYPE'],
                         '建檔日期': df['DATE_CREATED'], 'CA01': blank, 'CA02': blank,
                         'CA03': blank, 'CA04': blank, 'CA05': blank, 'CA06': blank,
                         'CA07': blank, 'CA08': blank, 'CB01': blank, 'CB02': blank,
                         'CB03': blank, 'CB04': blank, 'CC01': blank, 'CD01': blank,
                         'CD02': blank, '備註': blank, '定義': blank}
    service_info_df = pd.DataFrame(service_info_dict)
    income = list(zip(df['A3CH1'], df['A3CH2'], df['A3CH3'], df['A3CH7']))
    # convert_digit = (lambda x: int(x.split('.')[0]))
    population_dict = {'個案編號': case_no, '年度': converted_year, '年齡': blank, '性別': blank,
                       '教育程度': map(convert_digit, df['EDU_TYPE']), '婚姻狀況': map(convert_digit, df['MARRIAGE']),
                       '身份福利': map(convert_welfare, income), '居住狀況': map(convert_digit, df['H1A']),
                       '看護有無': map(lambda x: str_na if x == str_na else (0 if '無' in x else 1), df['LABOR_TYPE']),
                       '偏遠與否': map(lambda x: str_na if x == str_na else (1 if '偏遠地區' in x else 0), df['A5']),
                       '一般戶1': map(convert_yes_no, df['A3CH1']), '一般戶2': map(convert_yes_no, df['A3CH2']),
                       '低收': map(convert_yes_no, df['A3CH3']), '中低收': map(convert_yes_no, df['A3CH7'])}
    population_df = pd.DataFrame(population_dict)
    diseases_dict = get_converted_diseases_dict(df)
    diseases_num = get_diseases_num(diseases_dict, len(df))
    response_score = get_response_score(df[['D_RESP2', 'D_RESP3', 'D_RESP4']])
    health_status_dict = {'個案編號': case_no, '年度': converted_year,
                          '失能等級': map(lambda x: re.findall(r"\d", x)[0], df['CMS_LEV']), '主要疾病分類': blank,
                          '共病數目': diseases_num, '疼痛1': map(convert_digit, df['G1A']),
                          '疼痛2': map(convert_digit, df['G1B']), '疼痛乘積': blank,
                          '視力': map(convert_digit, df['VISION']), '聽力': map(convert_digit, df['HEARING']),
                          '表達能力': map(convert_digit, df['EXPRESSION']),
                          '理解能力': map(convert_digit, df['RECEPTION']),
                          '短期記憶2': map(convert_digit, df['D_RESP2']),
                          '短期記憶3': map(convert_digit, df['D_RESP3']),
                          '短期記憶4': map(convert_digit, df['D_RESP4']), '記憶總分': response_score}
    health_status_df = pd.DataFrame(health_status_dict)
    disease_items_dict = get_disease_items_dict(case_no, year, df)
    disease_items_df = pd.DataFrame(disease_items_dict)
    iadl_dict = {'個案編號': case_no, '年度': converted_year, '電話': map(convert_digit, df['USE_PHONE']),
                 '上街購物': map(convert_digit, df['SHOPPING']), '備餐': map(convert_digit, df['COOKING']),
                 '家務': map(convert_digit, df['HOUSEWORK'])}
    dfs = {'服務使用次數': service_info_df, '社會人口': population_df, '健康狀況': health_status_df,
           '共病項目': disease_items_df}
    excel_path = path.join(output_path, f'{year}_初評中介檔.xlsx')
    print('writing excel..... => ', excel_path)
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_name in dfs.keys():
            dfs[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == '__main__':
    start = time.time()
    # dir_name_years = os.listdir(config.data_sample_selected_path)
    # for dir_name_year in dir_name_years:
    #     os.listdir(path.join(config.data_sample_selected_path, dir_name_year))
    os.makedirs(config.data_output_tmp_path, exist_ok=True)
    for dir_year in Path(config.data_sample_selected_path).iterdir():
        year = dir_year.stem
        output_path = path.join(config.data_output_tmp_path, year)
        os.makedirs(output_path, exist_ok=True)
        for file in dir_year.iterdir():
            if 'pretest' in file.stem and file.suffix == '.pickle':
                with file.open('rb') as handle:
                    pretest_df = pd.DataFrame.from_dict(pickle.load(handle))
                    process_pretest(output_path, pretest_df, year)
            elif 'posttest' in file.stem and file.suffix == '.pickle':
                with file.open('rb') as handle:
                    posttest_df = pd.DataFrame.from_dict(pickle.load(handle))
    end = time.time()
    print('Elapsed time(sec) for output_tmp: ', end - start)
