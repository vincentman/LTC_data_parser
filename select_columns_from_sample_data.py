import pandas as pd
from os import path
import config
import pickle


def read_data_and_select_columns(data_pickle_path):
    keys_df = pd.read_excel('keys for 屏基.xlsx', index_col=None, engine='openpyxl')
    print('reading data pickle.....', data_pickle_path)
    with open(data_pickle_path, 'rb') as handle:
        data_pickle = pickle.load(handle)
    data_df = pd.DataFrame.from_dict(data_pickle)
    keys = keys_df.columns.values.tolist()
    keys_removed = ['H1a', 'G4B3WEIGH', 'G4B3DOT1', 'G4B3DOT2', 'G4B3DOT3', 'G4B3TALL']
    for key_removed in keys_removed:
        if key_removed in keys:
            keys.remove(key_removed)
    data_df = data_df[keys]
    return data_df


if __name__ == '__main__':
    input_pickle_path = path.join(config.data_sample_selected_path, config.data_sample_selected_pickle_name_hospital)
    data_df = read_data_and_select_columns(input_pickle_path)
    output_pickle_path = path.join(config.data_sample_selected_path, config.data_selected_pickle_name_hospital)
    with open(output_pickle_path, 'wb') as handle:
        print(f'writing pickle(count: {len(data_df)})..... => {output_pickle_path}')
        pickle.dump(data_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # get the newest: 僅抓取最新審核
    input_pickle_path = path.join(config.data_sample_selected_path,
                                  config.data_sample_selected_pickle_name_hospital_newest)
    data_df = read_data_and_select_columns(input_pickle_path)
    output_pickle_path = path.join(config.data_sample_selected_path, config.data_selected_pickle_name_hospital_newest)
    with open(output_pickle_path, 'wb') as handle:
        print(f'writing pickle(count: {len(data_df)})..... => {output_pickle_path}')
        pickle.dump(data_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
