import json
import os
import numpy as np
import pandas as pd

def json_to_yolo(data):
    yolo_format = []

    image_width = data["description"]["imageWidth"]
    image_height = data["description"]["imageHeight"]

    for annotation in data["annotations"].get("environment", []):
        # For polygon shapes in environment, currently skipping as YOLO uses bounding boxes
        pass

    for annotation in data["annotations"].get("PM", []):
        if annotation["shape_type"] == "bbox":
            x_center = (annotation["points"][0] + annotation["points"][2]) / 2 / image_width
            y_center = (annotation["points"][1] + annotation["points"][3]) / 2 / image_height
            width = (annotation["points"][2] - annotation["points"][0]) / image_width
            height = (annotation["points"][3] - annotation["points"][1]) / image_height

            yolo_format.append(f"{annotation['PM_code']} {x_center} {y_center} {width} {height}")

    return yolo_format


def convert_to_utf8(filepath):
    # 파일을 바이너리 모드로 읽습니다.
    with open(filepath, 'rb') as file:
        content = file.read()

    # utf-8로 다시 씁니다.
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content.decode('utf-8', 'ignore'))


def load_json_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_yolo_to_txt(yolo_data, filepath, json_filename):
    txt_filename = os.path.splitext(json_filename)[0] + ".txt"
    txt_filepath = os.path.join(filepath, txt_filename)
    with open(txt_filepath, 'w', encoding='utf-8') as f:
        for line in yolo_data:
            f.write(line + '\n')


def json_to_txt(label_path,txt_directory_path): #type =[0:실증,1:연출,2:블랙박스]
    all_data_list = []
    failed_files = []  # 에러가 발생한 파일 이름을 저장할 리스트
    filenames = list(os.listdir(label_path))
    for i in filenames:
        json_file_path = str(label_path + '/' + i)
        convert_to_utf8(json_file_path)
        json_filename = os.path.basename(json_file_path)
        
        try:
            data = load_json_from_file(json_file_path)
            yolo_annotations = json_to_yolo(data)
            save_yolo_to_txt(yolo_annotations, txt_directory_path, json_filename)

            for ann in yolo_annotations:
                ann = i + ann
                all_data_list.append(ann.split(' '))
        
        except json.JSONDecodeError:
            failed_files.append(i)
    print("Failed files:", failed_files)
    return all_data_list



label_path = input('라벨 경로를 입력하세요. :')
txt_directory_path = input('데이터 저장 경로를 입력하세요. :')
csv_name = input('csv 파일 명을 입력하세요 :')

all_data_list = json_to_txt(label_path,txt_directory_path)

df = pd.DataFrame(all_data_list, columns=['name', 'class', 'x_center', 'y_center', 'width', 'height'])

df['is_scripted'] = df['name'].apply(lambda x: x[:-5].split('_')[-1])
df['device'] = df['name'].apply(lambda x: x[:-5].split('_')[3])
df['time'] = df['name'].apply(lambda x: x[:-5].split('_')[4])
df['weather'] = df['name'].apply(lambda x: x[:-5].split('_')[5])
df['name'] = df['name'].apply(lambda x: x.split('.')[0])

df = df[['name','is_scripted', 'device', 'time', 'weather','x_center', 'y_center', 'width', 'height','class']]

df.to_csv(f'{csv_name}.csv', index=False)