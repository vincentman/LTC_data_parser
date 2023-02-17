import pandas as pd
import time
import pickle
from os import path
import os
import config
import sys
from pathlib import Path

if __name__ == '__main__':
    start = time.time()
    if sys.argv[1] == 'all_samples_data':
        file_name = config.sample_list_pickle_name
        folder_path = config.sample_list_serialized_path
        data_pickle_path = path.join(folder_path, file_name)
        print('reading data pickle.....', data_pickle_path)
        with open(data_pickle_path, 'rb') as handle:
            data_pickle = pickle.load(handle)
        data_df = pd.DataFrame.from_dict(data_pickle)
        output_excel_path = path.join(folder_path, f'{Path(file_name).stem}.xlsx')
        print(f'write excel(count: {len(data_df)}).....{output_excel_path}')
        data_df.to_excel(
            output_excel_path, index=False)

end = time.time()
print('Elapsed time(sec) for write_excel: ', end - start)
