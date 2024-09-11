import os
from manage_json_files import json_update


def convert_txt_to_json(path: str):
    files = os.listdir(path)
    txt_files = [file for file in files if '.txt' in file]
    print(f'txt_files = {txt_files}')
    print(f'len = {len(txt_files)}')

    for txt_file in txt_files:
        print(txt_file)
        with open(os.path.join(path, txt_file), 'r') as f:
            data_list = f.readlines()
        for data in data_list:
            data = data.strip()
            pos_name, class_name = data.split(':')
            json_update(
                os.path.join(path, txt_file.replace('.txt', '.json')),
                {pos_name: class_name}
            )
        os.remove(os.path.join(path, txt_file))


if __name__ == '__main__':
    convert_txt_to_json('data/D07 QM7-3238/img_full')
    convert_txt_to_json('data/D87 QM7-4643/img_full')
