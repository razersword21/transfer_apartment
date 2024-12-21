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
def make_memory(person_memory: str, person_name:str, time: str, content: str, label: str):
    if person_name == None:
        person_memory += time+" "+label+content+"\n"
    else:
        person_memory += time+" "+label+person_name+content+"\n"
    return person_memory

# 將感知寫到其他人記憶
def write_memory_for_all_observe(path: str, person_file_name: str, location: str, content: str, person_name:str):
    for file in os.listdir(path):
        if file.startswith("p") and (not file.startswith(person_file_name)):
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)

            if person_information['current_location'] == location:
                current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
                label = "[others]"
                
                person_information['memory'] = make_memory(person_information['memory'], person_name, current_time, content, label)
            
                with open(write_file_path+file, "w", encoding="utf-8") as f:
                    json.dump(person_information, f, ensure_ascii=False, indent=4)

def write_map_observe(map_data, person_info, action):
    map_data[person_info["current_location"]]['observe'].append({person_info['personality']['name'] : action})
    
    for location, value in map_data.items():
        if "nearbyPersons" in value:
            if person_info['personality']['name'] in value['nearbyPersons']:
                value['nearbyPersons'].remove(person_info['personality']['name'])

    map_data[person_info["current_location"]]['nearbyPersons'].append(person_info['personality']['name'])
    
    with open(write_file_path+"map_information.json", "w", encoding="utf-8") as f:
        json.dump(map_data, f, ensure_ascii=False, indent=4)

    return map_data



# 獲取地圖資料
def get_map_information(map_information, person_information):
    all_map_information = copy.deepcopy(map_information)
    try:
        observe = map_information[person_information["current_location"]]['observe']
    except:
        observe = []
    data_without_observe, location_name_list, all_location_object = remove_observe(map_information)
    
    return observe, data_without_observe, location_name_list, all_location_object, all_map_information

def remove_observe(data):
    locations = []
    data_without_observe = copy.deepcopy(data)  # 创建深拷贝
    all_location_information = {}
    for location, items in data_without_observe.items():
        if "observe" in items:
            del items["observe"]
        if "nearbyPersons" in items:
            del items["nearbyPersons"]
        locations.append(location)
        all_location_information[location] = {key for key, value in items.items()}
    
    return data_without_observe, locations, all_location_information


def used_object(person_information, action, all_map_information):
    person_information['current_location'] = action['location']
    if action['object'] != "Nothing":
        all_map_information[person_information['current_location']][action['object']] -= 1
    if len(person_information['current_object']) != 0 and person_information['current_object'] != "Nothing":
        all_map_information[person_information['current_location']][person_information['current_object']] += 1
    person_information['current_object'] = action['object']
    return person_information, all_map_information

# 檢查動作是否有效
def check_action_valid(action, all_location_object, all_map_information):
    if action['location'] in all_location_object:
        if action['object'] in all_location_object[action['location']]:
            if all_map_information[action['location']][action['object']] > 0:
                return True, " 動作有效"
            else:
                return False, " 物件已經被占用"
        elif action['object'] == "Nothing":
            return True, " 沒有使用物件"
        else:
            return False, " 物件不存在"
    return False, " 地點不存在"
