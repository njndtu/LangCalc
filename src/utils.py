import json
import os

from conf.settings import (
    DATA_PATH
)




def save_as_jsonl(data, name_of_file):
    '''
    input:
        data (list[json]) : input data to be saved
        path (str) : path to save jsonl
    '''

    path_to_save = os.path.join(DATA_PATH, name_of_file)
    with open(path_to_save, "w") as f:
        
        for i in data:
            f.write(json.dumps(i, ensure_ascii=False)+"\n")
