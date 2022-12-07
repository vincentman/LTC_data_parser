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
convert_adl_score_2items = (lambda x: (2 - x) * 5)
convert_adl_score_3items = (lambda x: (3 - x) * 5)
convert_adl_score_4items = (lambda x: (4 - x) * 5)
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
    for i in range(disease_item_num):
        key = f'G4E_CH{i + 1}'
        disease_df = df[key].replace({'1.是': 1, '2.否': 0})
        diseases_dict[key] = disease_df
    return diseases_dict


def get_diseases_num(converted_diseases_dict, data_length):
    blank = [0] * data_length
    column_name = 'diseases_num'
    diseases_num_df = pd.DataFrame(blank, columns=[column_name])
    for i in range(disease_item_num):
        diseases_num_df[column_name] = np.squeeze(diseases_num_df.values) + converted_diseases_dict[
            f'G4E_CH{i + 1}'].values
    return diseases_num_df[column_name].tolist()


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


def get_response_score(df, keys):
    response_score_df = pd.DataFrame()
    convert_response_score = (lambda x: str_na if x == str_na else (1 if x == 1 else 0))
    for key in keys:
        tmp_df = df[key].apply(convert_digit)
        response_score_df[key] = tmp_df.apply(convert_response_score)
    return response_score_df.sum(axis=1).apply(lambda x: x if str(x).isnumeric() else str_na)


class OutputTmp:
    def __init__(self, year, df):
        self.year = year
        self.df = df
        self.df.fillna(str_na, inplace=True)
        self.blank = [''] * len(self.df)
        print(f'資料筆數： {len(self.df)}')
        self.case_no = self.df['CASENO']
        self.converted_year = list(map(lambda x: x.year - 1911, self.df['DATE_CREATED']))

    def process_pretest(self):
        service_info_dict = {'個案編號': self.case_no, '年度': self.converted_year,
                             '類別': self.df['PLAN_TYPE'],
                             '建檔日期': self.df['DATE_CREATED'], 'CA01': self.blank, 'CA02': self.blank,
                             'CA03': self.blank, 'CA04': self.blank, 'CA05': self.blank, 'CA06': self.blank,
                             'CA07': self.blank, 'CA08': self.blank, 'CB01': self.blank, 'CB02': self.blank,
                             'CB03': self.blank, 'CB04': self.blank, 'CC01': self.blank, 'CD01': self.blank,
                             'CD02': self.blank, '備註': self.blank, '定義': self.blank}
        service_info_df = pd.DataFrame(service_info_dict)
        income = list(zip(self.df['A3CH1'], self.df['A3CH2'], self.df['A3CH3'], self.df['A3CH7']))
        population_dict = {'個案編號': self.case_no, '年度': self.converted_year, '年齡': self.blank,
                           '性別': self.blank,
                           '教育程度': map(convert_digit, self.df['EDU_TYPE']),
                           '婚姻狀況': map(convert_digit, self.df['MARRIAGE']),
                           '身份福利': map(convert_welfare, income), '居住狀況': map(convert_digit, self.df['H1A']),
                           '看護有無': map(lambda x: str_na if x == str_na else (0 if '無' in x else 1),
                                           self.df['LABOR_TYPE']),
                           '偏遠與否': map(lambda x: str_na if x == str_na else (1 if '偏遠地區' in x else 0),
                                           self.df['A5']),
                           '一般戶1': map(convert_yes_no, self.df['A3CH1']),
                           '一般戶2': map(convert_yes_no, self.df['A3CH2']),
                           '低收': map(convert_yes_no, self.df['A3CH3']),
                           '中低收': map(convert_yes_no, self.df['A3CH7'])}
        population_df = pd.DataFrame(population_dict)
        converted_diseases_dict = get_converted_diseases_dict(self.df)
        diseases_num = get_diseases_num(converted_diseases_dict, len(self.df))
        response_score = get_response_score(self.df, ['D_RESP2', 'D_RESP3', 'D_RESP4'])
        health_status_dict = {'個案編號': self.case_no, '年度': self.converted_year,
                              '失能等級': map(lambda x: re.findall(r"\d", x)[0], self.df['CMS_LEV']),
                              '主要疾病分類': self.blank,
                              '共病數目': diseases_num, '疼痛1': map(convert_digit, self.df['G1A']),
                              '疼痛2': map(convert_digit, self.df['G1B']), '疼痛乘積': self.blank,
                              '視力': map(convert_digit, self.df['VISION']),
                              '聽力': map(convert_digit, self.df['HEARING']),
                              '表達能力': map(convert_digit, self.df['EXPRESSION']),
                              '理解能力': map(convert_digit, self.df['RECEPTION']),
                              '短期記憶2': map(convert_digit, self.df['D_RESP2']),
                              '短期記憶3': map(convert_digit, self.df['D_RESP3']),
                              '短期記憶4': map(convert_digit, self.df['D_RESP4']), '記憶總分': response_score}
        health_status_df = pd.DataFrame(health_status_dict)
        disease_items_dict = get_disease_items_dict(self.case_no, self.converted_year, self.df)
        disease_items_df = pd.DataFrame(disease_items_dict)
        adl_dict = {'個案編號': self.case_no, '年度': self.converted_year, '進食': map(convert_digit, self.df['E_EAT']),
                    '洗澡': map(convert_digit, self.df['E_BATH']),
                    '修飾': map(convert_digit, self.df['E_ADORN']),
                    '穿脫衣': map(convert_digit, self.df['E_WEAR']),
                    '排便': map(convert_digit, self.df['E_STOOL']),
                    '排尿': map(convert_digit, self.df['E_URINE']),
                    '如廁': map(convert_digit, self.df['E_TOILET']),
                    '移位': map(convert_digit, self.df['E_MOVE']),
                    '步行': map(convert_digit, self.df['E_WALK']),
                    '上下樓': map(convert_digit, self.df['E_STAIRS']),
                    '位移能力': map(convert_digit, self.df['E11'])}
        adl_df = pd.DataFrame(adl_dict)
        adl_2items_score_dt = adl_df[['洗澡', '修飾']].apply(convert_adl_score_2items)
        adl_3items_score_dt = adl_df[['進食', '穿脫衣', '排便', '排尿', '如廁', '上下樓']].apply(
            convert_adl_score_3items)
        adl_4items_score_dt = adl_df[['移位', '步行']].apply(convert_adl_score_4items)
        adl_sum = adl_2items_score_dt.sum(axis=1) + adl_3items_score_dt.sum(axis=1) + adl_4items_score_dt.sum(axis=1)
        iadl_dict = {'個案編號': self.case_no, '年度': self.converted_year,
                     '電話': map(convert_digit, self.df['USE_PHONE']),
                     '上街購物': map(convert_digit, self.df['SHOPPING']),
                     '備餐': map(convert_digit, self.df['COOKING']),
                     '家務': map(convert_digit, self.df['HOUSEWORK']), '洗衣': map(convert_digit, self.df['CLEANING']),
                     '外出': map(convert_digit, self.df['OUT_ACTION']), '服藥': map(convert_digit, self.df['TAKE_MDC']),
                     '財務': map(convert_digit, self.df['FINANCE'])}
        iadl_df = pd.DataFrame(iadl_dict)
        iadl_sum = iadl_df[['電話', '上街購物', '備餐', '家務', '洗衣', '外出', '服藥', '財務']].sum(axis=1)
        caregiver_load_dict = {'個案編號': self.case_no, '年度': self.converted_year,
                               '睡眠': map(convert_yes_no, self.df['JJ1']),
                               '體力': map(convert_yes_no, self.df['J2']),
                               '其他家人': map(convert_yes_no, self.df['J3']),
                               '困擾行為': map(convert_yes_no, self.df['J4']),
                               '壓力': map(convert_yes_no, self.df['J5'])}
        caregiver_load_df = pd.DataFrame(caregiver_load_dict)
        caregiver_load_sum = caregiver_load_df[['睡眠', '體力', '其他家人', '困擾行為', '壓力']].sum(axis=1).apply(
            lambda x: x if str(x).isnumeric() else str_na)
        estimation_dict = {'個案編號': self.case_no, '年度': self.converted_year, 'ADL': adl_sum, 'IADL': iadl_sum,
                           '失能等級': map(lambda x: re.findall(r"\d", x)[0], self.df['CMS_LEV']),
                           '照顧者負荷': caregiver_load_sum,
                           '目標達成率': self.blank}
        estimation_df = pd.DataFrame(estimation_dict)
        pretest_dfs = {'服務使用次數': service_info_df, '社會人口': population_df, '健康狀況': health_status_df,
                       '共病項目': disease_items_df, 'ADL': adl_df, 'IADL': iadl_df, '照顧者負荷': caregiver_load_df,
                       '成效評估整理': estimation_df}
        excel_path = path.join(config.data_output_tmp_path, f'{year}_初評中介檔.xlsx')
        print('writing excel..... => ', excel_path)
        with pd.ExcelWriter(excel_path) as writer:
            for sheet_name in pretest_dfs.keys():
                pretest_dfs[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == '__main__':
    start = time.time()
    # 以建檔年份(108~111)，初評為條件 => 初評中介檔，取得案號
    years = ['108', '109', '110', '111']
    with open(path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name), 'rb') as handle:
        all_df = pd.DataFrame.from_dict(pickle.load(handle))
    os.makedirs(config.data_output_tmp_path, exist_ok=True)
    for year in years:
        ce_year = int(year) + 1911
        pretest_df = all_df[(all_df['DATE_CREATED'].dt.year == ce_year) & (all_df['PLAN_TYPE'] == '初評')]
        pretest_df.drop_duplicates(subset=['CASENO'], keep='first', inplace=True)
        print('Process pretest, year: ', year)
        output_obj = OutputTmp(year, pretest_df)
        output_obj.process_pretest()
    # 依初評所得案號，取出複評，再以案號、建檔日期為條件做排序，取出第一筆複評 => 複評中介檔
    end = time.time()
    print('Elapsed time(sec) for output_tmp: ', end - start)
