import json
import re
import os
import copy
import time
from datetime import datetime

from config_new import *

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

# 記憶格式
def make_memory(person_memory: str, time: str, content: str, label: str):
    person_memory += time+" "+label+content+"\n"
    return person_memory

# 將感知寫到其他人記憶
def write_memory_for_all_observe(path: str, person_file_name: str, location: str, content: str):
    for file in os.listdir(path):
        if file.startswith("p") and (not file.startswith(person_file_name)):
            
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
            if person_information['current_location'] == location:
                current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
                label = "[others]"
                person_information['memory']  = make_memory(person_information['memory'], current_time, content, label)
            
            with open(write_file_path+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)

def write_map_observe(map_data, person_info, action):
    map_data[person_info["current_location"]]['observe'].append(person_info['background']['name']+action)
    with open(write_file_path+"map_information.json", "w", encoding="utf-8") as f:
        json.dump(map_data, f, ensure_ascii=False, indent=4)

def remove_observe(data):
    locations = []
    for location, items in data.items():
        if "observe" in items:
            del items["observe"]
        locations.append(location)
    locations.append("其他地方")
    return data, locations

# 獲取地圖資料
def get_observe(map_information, person_information):
    all_map_information = copy.deepcopy(map_information)
    observe = map_information[person_information["current_location"]]
    map_info, location_list = remove_observe(map_information)
    return observe, map_info, location_list, all_map_information

def write_current_location_and_used_object(person_information, transfered_action, all_map_information):
    person_information["current_location"] = transfered_action["location"]
    if transfered_action['object'] != None and all_map_information[person_information["current_location"]][transfered_action['object']] > 0:
        all_map_information[person_information["current_location"]][transfered_action['object']] -= 1
    return person_information, all_map_information