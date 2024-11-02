import json
import re
import os
import time
from datetime import datetime

def check_json_format(data: str, flag: bool):
    try:
        result = json.loads(data)
        flag = True
    except json.JSONDecodeError:
        try:
            json_string = re.search(r"```json(.*)```", data, re.DOTALL).group(1).strip()
            result = json.loads(json_string)
            flag = True
        except (json.JSONDecodeError, AttributeError):
            result = None
    return result, flag

def write_memory(person_memory: str, time: str, content: str, label: str):
    person_memory += time+" "+label+content+"\n"
    return person_memory

def write_memory_for_all_observe(path: str, person_file_name: str, location: str, content: str):
    for file in os.listdir(path):
        if file.startswith("p") and (not file.startswith(person_file_name)):
            
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
            if person_information['current_location'] == location:
                current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
                label = "[others]"
                person_information['memory']  = write_memory(person_information['memory'], current_time, content, label)
            
            with open("C:/Users/user/Desktop/setiproject/personal_information/"+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)

def remove_observe(data):
    # 如果是字典，處理每個鍵值對
    if isinstance(data, dict):
        # 創建新字典，排除 'observe' 鍵
        return {k: remove_observe(v) for k, v in data.items() if k != 'observe'}
    # 如果是列表，遞迴處理每個元素
    elif isinstance(data, list):
        return [remove_observe(x) for x in data]
    # 如果是其他類型，直接返回
    else:
        return data
    
