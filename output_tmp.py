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
# convert_digit_nan_0 = (lambda x: 0 if x == str_na else (int(x.split('.')[0])))
convert_adl_score_2items = (lambda x: (2 - x) * 5)
convert_adl_score_3items = (lambda x: (3 - x) * 5)
convert_adl_score_4items = (lambda x: (4 - x) * 5)
disease_item_num = 24


def convert_welfare_old(income):
    if income[0] == '是':
        return int(1)
    if income[1] == '是':
        return int(2)
    if income[2] == '是':
        return int(3)
    if income[3] == '是':
        return int(4)


def convert_welfare(income):
    if income == '未達1倍':
        return 1
    if income == '未達1.5倍':
        return 2
    if income == '1.5~2.5倍':
        return 3
    if income == '一般':
        return 4


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


def get_response_score(df, keys):
    response_score_df = pd.DataFrame()
    convert_response_score = (lambda x: str_na if x == str_na else (1 if x == 1 else 0))
    for key in keys:
        tmp_df = df[key].apply(convert_digit)
        response_score_df[key] = tmp_df.apply(convert_response_score)
    return response_score_df.sum(axis=1).apply(lambda x: x if str(x).isnumeric() else str_na)


def get_disease_items_dict(df):
    disease_items_dict = {'1高血壓': map(convert_yes_no, df['G4E_CH1']),
                          '2糖尿病': map(convert_yes_no, df['G4E_CH2']),
                          '3骨骼系統': map(convert_yes_no, df['G4E_CH3']),
                          '4視覺疾病': map(convert_yes_no, df['G4E_CH4']),
                          '5中風': map(convert_yes_no, df['G4E_CH5']),
                          '6冠狀動脈': map(convert_yes_no, df['G4E_CH6']),
                          '7心房節律': map(convert_yes_no, df['G4E_CH7']),
                          '8癌症': map(convert_yes_no, df['G4E_CH8']),
                          '9呼吸系統': map(convert_yes_no, df['G4E_CH9']),
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
                          '22罕病': map(convert_yes_no, df['G4E_CH22']),
                          '23癲癇': map(convert_yes_no, df['G4E_CH23']),
                          '24其他': map(convert_yes_no, df['G4E_CH24'])}
    return disease_items_dict


def get_adl_score(adl_dict, is_pretest):
    pre_post_test_str = '初' if is_pretest else '複'
    adl_df = pd.DataFrame(adl_dict)
    adl_2items_score_dt = adl_df[[f'{pre_post_test_str}洗澡', f'{pre_post_test_str}修飾']].apply(
        convert_adl_score_2items)
    adl_3items_score_dt = adl_df[
        [f'{pre_post_test_str}進食', f'{pre_post_test_str}穿脫衣', f'{pre_post_test_str}排便',
         f'{pre_post_test_str}排尿', f'{pre_post_test_str}如廁', f'{pre_post_test_str}上下樓']].apply(
        convert_adl_score_3items)
    adl_4items_score_dt = adl_df[[f'{pre_post_test_str}移位', f'{pre_post_test_str}步行']].apply(
        convert_adl_score_4items)
    adl_score = adl_2items_score_dt.sum(axis=1) + adl_3items_score_dt.sum(axis=1) + adl_4items_score_dt.sum(axis=1)
    return adl_score


def get_iadl_score(iadl_dict, is_pretest):
    pre_post_test_str = '初' if is_pretest else '複'
    iadl_df = pd.DataFrame(iadl_dict)
    iadl_score = iadl_df[[f'{pre_post_test_str}電話', f'{pre_post_test_str}上街購物', f'{pre_post_test_str}備餐',
                          f'{pre_post_test_str}家務', f'{pre_post_test_str}洗衣', f'{pre_post_test_str}外出',
                          f'{pre_post_test_str}服藥', f'{pre_post_test_str}財務']].sum(axis=1)
    return iadl_score


def get_caregiver_load_score(caregiver_load_dict, is_pretest):
    pre_post_test_str = '初' if is_pretest else '複'
    caregiver_load_df = pd.DataFrame(caregiver_load_dict)
    for col in caregiver_load_df.columns:  # to_numeric: string will be converted as nan
        caregiver_load_df[col] = pd.to_numeric(caregiver_load_df[col], errors='coerce', downcast='integer')
    # caregiver_load_df = caregiver_load_df.astype('int32', errors='ignore')
    caregiver_load_score = caregiver_load_df[
        [f'{pre_post_test_str}睡眠', f'{pre_post_test_str}體力', f'{pre_post_test_str}其他家人',
         f'{pre_post_test_str}困擾行為', f'{pre_post_test_str}壓力']].sum(skipna=False, axis=1).apply(
        lambda x: int(x) if not np.isnan(x) else str_na)
    return caregiver_load_score


class OutputTmp:
    def __init__(self, df, posttest_df, sample_df):
        self.df = df
        self.posttest_df = posttest_df
        self.sample_df = sample_df
        self.df.fillna(str_na, inplace=True)
        self.posttest_df.fillna(str_na, inplace=True)
        self.blank = [''] * len(self.df)
        self.col_str_na = [str_na] * len(self.df)
        self.df['CASENO'] = self.df['CASENO'].apply(str)
        self.sample_df['案號'] = self.sample_df['案號'].apply(str)
        self.converted_year = list(map(lambda x: int(x[:4]) - 1911, self.df['DATE_CREATED']))
        self.df = pd.merge(self.df, self.sample_df[['案號', '姓名', '身分證號', '年齡', '福利身分']], left_on='CASENO',
                           right_on='案號').drop('案號', axis=1)

    def get_adl_dict(self, df, is_pretest):
        pre_post_test_str = '初' if is_pretest else '複'
        adl_dict = {
            f'{pre_post_test_str}進食': list(map(convert_digit, df['E_EAT'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}洗澡': list(map(convert_digit, df['E_BATH'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}修飾': list(map(convert_digit, df['E_ADORN'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}穿脫衣': list(map(convert_digit, df['E_WEAR'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}排便': list(map(convert_digit, df['E_STOOL'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}排尿': list(map(convert_digit, df['E_URINE'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}如廁': list(map(convert_digit, df['E_TOILET'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}移位': list(map(convert_digit, df['E_MOVE'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}步行': list(map(convert_digit, df['E_WALK'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}上下樓': list(map(convert_digit, df['E_STAIRS'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}位移能力': list(map(convert_digit, df['E11'])) if not df.empty else self.col_str_na}
        return adl_dict

    def get_iadl_dict(self, df, is_pretest):
        pre_post_test_str = '初' if is_pretest else '複'
        iadl_dict = {
            f'{pre_post_test_str}電話': list(map(convert_digit, df['USE_PHONE'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}上街購物': list(
                map(convert_digit, df['SHOPPING'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}備餐': list(map(convert_digit, df['COOKING'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}家務': list(map(convert_digit, df['HOUSEWORK'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}洗衣': list(map(convert_digit, df['CLEANING'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}外出': list(map(convert_digit, df['OUT_ACTION'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}服藥': list(map(convert_digit, df['TAKE_MDC'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}財務': list(map(convert_digit, df['FINANCE'])) if not df.empty else self.col_str_na}
        return iadl_dict

    def get_caregiver_load_dict(self, df, is_pretest):
        pre_post_test_str = '初' if is_pretest else '複'
        caregiver_load_dict = {
            f'{pre_post_test_str}睡眠': list(map(convert_yes_no, df['JJ1'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}體力': list(map(convert_yes_no, df['J2'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}其他家人': list(map(convert_yes_no, df['J3'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}困擾行為': list(map(convert_yes_no, df['J4'])) if not df.empty else self.col_str_na,
            f'{pre_post_test_str}壓力': list(map(convert_yes_no, df['J5'])) if not df.empty else self.col_str_na}
        return caregiver_load_dict

    def get_summary(self):
        summary = dict()
        convert_age = (lambda x: int(x.split('歲')[0]))
        convert_gender = (lambda x: 1 if x[1] == '1' else 2)
        basic_info_dict = {'個案編號': self.df['CASENO'], '初評建檔日期': self.df['DATE_CREATED'],
                           '年度': self.converted_year, '定義': self.blank,
                           '姓名': self.df['姓名'], '年齡': list(map(convert_age, self.df['年齡'])),
                           '性別': list(map(convert_gender, self.df['身分證號']))}
        summary.update(basic_info_dict)
        population_dict = {'教育程度': list(map(convert_digit, self.df['EDU_TYPE'])),
                           '婚姻狀況': list(map(convert_digit, self.df['MARRIAGE'])),
                           '福利身分': list(map(convert_welfare, self.df['福利身分'])),
                           '居住狀況': list(map(convert_digit, self.df['H1A'])),
                           '看護有無': list(map(lambda x: str_na if x == str_na else (0 if '無' in x else 1),
                                            self.df['LABOR_TYPE'])),
                           '偏遠與否': list(map(lambda x: str_na if x == str_na else (1 if '偏遠地區' in x else 0),
                                            self.df['A5']))}
        summary.update(population_dict)
        converted_diseases_dict = get_converted_diseases_dict(self.df)
        diseases_num = get_diseases_num(converted_diseases_dict, len(self.df))
        response_score = get_response_score(self.df, ['D_RESP2', 'D_RESP3', 'D_RESP4'])
        convert_disability_level = (lambda x: str_na if x == str_na else re.findall(r"\d", x)[0])
        pretest_disability_level = list(map(convert_disability_level, self.df['CMS_LEV']))
        health_status_dict = {'失能等級': pretest_disability_level,
                              '主要疾病分類': self.blank,
                              '共病數目': diseases_num, '初身高': self.df['TALL'],
                              '初體重': self.df['WEIGH'],
                              '疼痛1': list(map(convert_digit, self.df['G1A'])),
                              '疼痛2': list(map(convert_digit, self.df['G1B'])), '疼痛乘積': self.blank,
                              '視力': list(map(convert_digit, self.df['VISION'])),
                              '聽力': list(map(convert_digit, self.df['HEARING'])),
                              '表達能力': list(map(convert_digit, self.df['EXPRESSION'])),
                              '理解能力': list(map(convert_digit, self.df['RECEPTION'])),
                              '初短期記憶2': list(map(convert_digit, self.df['D_RESP2'])),
                              '初短期記憶3': list(map(convert_digit, self.df['D_RESP3'])),
                              '初短期記憶4': list(map(convert_digit, self.df['D_RESP4'])), '初記憶總分': response_score}
        summary.update(health_status_dict)
        disease_items_dict = get_disease_items_dict(self.df)
        summary.update(disease_items_dict)
        pretest_adl_dict = self.get_adl_dict(self.df, True)
        summary.update(pretest_adl_dict)
        pretest_iadl_dict = self.get_iadl_dict(self.df, True)
        summary.update(pretest_iadl_dict)
        pretest_caregiver_load_dict = self.get_caregiver_load_dict(self.df, True)
        summary.update(pretest_caregiver_load_dict)
        pretest_estimation_dict = {'初ADL總分': get_adl_score(pretest_adl_dict, True),
                                   '初IADL總分': get_iadl_score(pretest_iadl_dict, True),
                                   '初失能等級': pretest_disability_level,
                                   '初照顧者負荷總分': get_caregiver_load_score(pretest_caregiver_load_dict, True),
                                   '目標達成率': self.blank}
        summary.update(pretest_estimation_dict)
        posttest_date_created = list(
            self.posttest_df['DATE_CREATED']) if not self.posttest_df.empty else self.col_str_na
        posttest_tall = list(self.posttest_df['TALL']) if not self.posttest_df.empty else self.col_str_na
        posttest_weight = list(self.posttest_df['WEIGH']) if not self.posttest_df.empty else self.col_str_na
        posttest_ache1 = list(
            map(convert_digit, self.posttest_df['G1A'])) if not self.posttest_df.empty else self.col_str_na
        posttest_ache2 = list(
            map(convert_digit, self.posttest_df['G1B'])) if not self.posttest_df.empty else self.col_str_na
        posttest_resp2 = list(
            map(convert_digit, self.posttest_df['D_RESP2'])) if not self.posttest_df.empty else self.col_str_na
        posttest_resp3 = list(
            map(convert_digit, self.posttest_df['D_RESP3'])) if not self.posttest_df.empty else self.col_str_na
        posttest_resp4 = list(
            map(convert_digit, self.posttest_df['D_RESP4'])) if not self.posttest_df.empty else self.col_str_na
        posttest_response_score = get_response_score(self.posttest_df, ['D_RESP2', 'D_RESP3',
                                                                        'D_RESP4']).tolist() \
            if not self.posttest_df.empty else self.col_str_na
        posttest_health_status_dict = {'複評建檔日期': posttest_date_created, '複身高': posttest_tall,
                                       '複體重': posttest_weight, '複疼痛1': posttest_ache1,
                                       '複疼痛2': posttest_ache2, '複短期記憶2': posttest_resp2,
                                       '複短期記憶3': posttest_resp3, '複短期記憶4': posttest_resp4,
                                       '複記憶總分': posttest_response_score}
        summary.update(posttest_health_status_dict)
        posttest_adl_dict = self.get_adl_dict(self.posttest_df, False)
        summary.update(posttest_adl_dict)
        posttest_iadl_dict = self.get_iadl_dict(self.posttest_df, False)
        summary.update(posttest_iadl_dict)
        posttest_caregiver_load_dict = self.get_caregiver_load_dict(self.posttest_df, False)
        summary.update(posttest_caregiver_load_dict)
        posttest_estimation_dict = {
            '複ADL總分': get_adl_score(posttest_adl_dict, False) if not self.posttest_df.empty else self.col_str_na,
            '複IADL總分': get_iadl_score(posttest_iadl_dict, False) if not self.posttest_df.empty else self.col_str_na,
            '複失能等級': list(map(convert_disability_level,
                              self.posttest_df['CMS_LEV'])) if not self.posttest_df.empty else self.col_str_na,
            '複照顧者負荷總分': get_caregiver_load_score(posttest_caregiver_load_dict,
                                                 False) if not self.posttest_df.empty else self.col_str_na}
        summary.update(posttest_estimation_dict)
        output_df = pd.DataFrame(summary)
        return output_df


def output_loss_final_caseno_list(all_sample_caseno_list, final_sample_caseno_list):
    loss_final_caseno_list = check_if_b_contained_in_a(all_sample_caseno_list, final_sample_caseno_list)
    print(f'不在名冊裡的最終名單: {len(loss_final_caseno_list)}筆')
    if len(loss_final_caseno_list) > 0:
        with pd.ExcelWriter(path.join(config.sample_select_list_path, '不在名冊裡的最終名單.xlsx'), engine='openpyxl') as writer:
            loss_final_caseno_list.to_excel(writer, sheet_name="遺失案號", index=False)


def get_final_sample_list_df(all_sample_list_df):
    final_caseno_list_file_path = path.join(config.sample_select_list_path,
                                            config.final_caseno_list_file_name)
    final_caseno_list_df = pd.read_excel(final_caseno_list_file_path, index_col=None, engine='openpyxl')
    print(f'reading final caseno list(count: {len(final_caseno_list_df)})..... => {final_caseno_list_file_path}')
    all_sample_list_df['案號'] = all_sample_list_df['案號'].apply(str)
    final_caseno_list_df['案號'] = final_caseno_list_df['案號'].apply(str)
    all_sample_caseno_list = all_sample_list_df['案號']
    final_sample_caseno_list = final_caseno_list_df['案號']
    output_loss_final_caseno_list(all_sample_caseno_list, final_sample_caseno_list)
    return all_sample_list_df[all_sample_caseno_list.isin(final_sample_caseno_list)]


def check_if_b_contained_in_a(a, b):
    """
    check if b is all contained in a
    :param a:
    :param b:
    :return: b not contained in a
    """
    b_found_in_a = b[b.isin(a)]
    tmp = pd.concat([b_found_in_a, b], axis=0)
    return tmp.drop_duplicates(keep=False)


def check_final_sample_list_match_output(output_caseno_list):
    final_caseno_list_file_path = path.join(config.sample_select_list_path,
                                            config.final_caseno_list_file_name)
    final_caseno_list_df = pd.read_excel(final_caseno_list_file_path, index_col=None, engine='openpyxl')
    print(
        f'final check ~~ reading final caseno list(count: {len(final_caseno_list_df)})..... => {final_caseno_list_file_path}')
    final_caseno_list = final_caseno_list_df['案號'].apply(str)
    loss_final_caseno_list = check_if_b_contained_in_a(output_caseno_list, final_caseno_list)
    print(f'不在Output裡的最終名單: {len(loss_final_caseno_list)}筆')
    if len(loss_final_caseno_list) > 0:
        with pd.ExcelWriter(path.join(config.sample_select_list_path, '不在Output裡的最終名單.xlsx'),
                            engine='openpyxl') as writer:
            loss_final_caseno_list.to_excel(writer, sheet_name="遺失案號", index=False)


if __name__ == '__main__':
    start = time.time()
    with open(path.join(config.sample_list_serialized_path, config.sample_list_pickle_name), 'rb') as handle:
        all_sample_list_df = pd.DataFrame.from_dict(pickle.load(handle))
    all_sample_list_df = get_final_sample_list_df(all_sample_list_df)
    all_sample_list_df.drop_duplicates(subset=['案號'], keep='first', inplace=True)  # 2967筆
    print(f'最終個案筆數： {len(all_sample_list_df)}')  # 2426筆
    with open(path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name), 'rb') as handle:
        all_df = pd.DataFrame.from_dict(pickle.load(handle))
    all_df.drop_duplicates(inplace=True)  # 4402筆
    print(f'全部資料筆數： {len(all_df)}')
    os.makedirs(config.data_output_tmp_path, exist_ok=True)
    all_pre_caseno = all_df[all_df['PLAN_TYPE'] == '初評']['CASENO']
    has_post_posttest_df = all_df[(all_df['CASENO'].isin(all_pre_caseno)) & (all_df['PLAN_TYPE'] == '複評')]
    has_post_posttest_df = has_post_posttest_df.sort_values(['CASENO', 'DATE_CREATED'])
    has_post_posttest_df.drop_duplicates(subset=['CASENO'], keep='first', inplace=True)  # 有做複評的複評資料
    has_post_caseno = has_post_posttest_df['CASENO']  # 有做複評的案號: 1153筆
    print('有做複評案號的筆數： ', len(has_post_caseno))
    has_post_pretest_df = all_df[(all_df['CASENO'].isin(has_post_caseno)) & (all_df['PLAN_TYPE'] == '初評')]
    has_post_pretest_df = has_post_pretest_df.sort_values(['CASENO'])  # 有做複評的初評資料
    tmp_concat_caseno = pd.concat([all_pre_caseno, has_post_caseno], axis=0)
    no_post_caseno = tmp_concat_caseno.drop_duplicates(keep=False)  # 只做初評(沒做複評)的案號: 1029筆
    print('沒做複評案號的筆數： ', len(no_post_caseno))
    no_post_pretest_df = all_df[(all_df['CASENO'].isin(no_post_caseno)) & (all_df['PLAN_TYPE'] == '初評')]
    no_post_pretest_df = no_post_pretest_df.sort_values(['CASENO'])  # 只做初評(沒做複評)的資料
    has_post_output_df = OutputTmp(has_post_pretest_df, has_post_posttest_df, all_sample_list_df).get_summary()
    print('有做複評的總表，筆數： ', len(has_post_output_df))
    no_post_output_df = OutputTmp(no_post_pretest_df, pd.DataFrame(), all_sample_list_df).get_summary()
    print('沒做複評的總表，筆數： ', len(no_post_output_df))
    all_output_df = pd.concat([has_post_output_df, no_post_output_df])
    all_output_df = all_output_df.sort_values(['個案編號'])  # 全部總表：2182筆
    print('全部總表，筆數： ', len(all_output_df))
    all_output_path = path.join(config.data_output_tmp_path, '全部總表.xlsx')
    print('writing excel..... => ', all_output_path)
    with pd.ExcelWriter(all_output_path, engine='openpyxl') as writer:
        all_output_df.to_excel(writer, sheet_name="總表", index=False)
    end = time.time()
    print('Elapsed time(sec) for output_tmp: ', end - start)
