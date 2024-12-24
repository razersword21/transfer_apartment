from model import *
from prompt_new import *
from method import *
from config_new import *
from action_method import *
from character_system import *

import shutil

def default_setting():
    # 將在file_path中的json檔案複製到write_file_path 正式遊戲時不使用
    for file in os.listdir(file_path):
        shutil.copy(file_path+file, write_file_path+file)
    
    # 初始化地图
    map_manager = MapManager()
    map_manager.load_map(write_file_path)
    
    # 初始化角色系统
    with open(write_file_path+"p1_information.json", "r", encoding="utf-8") as f:
        person_information = json.load(f)
    character1 = CharacterManager(person_information)

    with open(write_file_path+"p2_information.json", "r", encoding="utf-8") as f:
        person_information = json.load(f)
    character2 = CharacterManager(person_information)

    with open(write_file_path+"p3_information.json", "r", encoding="utf-8") as f:
        person_information = json.load(f)
    character3 = CharacterManager(person_information)

    map_manager.map_default_setting(character1, character2, character3)

    return map_manager, character1, character2, character3

def main():
    map_manager, character1, character2, character3 = default_setting()
    character_dict = {
        character1.name: character1,
        character2.name: character2,
        character3.name: character3
    }

    # character1.decision.init_schedule(character1.memory.person_memory)
    # character2.decision.init_schedule(character2.memory.person_memory)
    # character3.decision.init_schedule(character3.memory.person_memory)
    # print(f"人物1行程表: {character1.decision.current_schedule}")

    print(f"Init map data {map_manager.map_data}")
    location_list = map_manager.get_list_of_locations()
    all_location_object = map_manager.get_list_of_all_objects()
    
    map_data, interactive_character_name, action = character1.character_action(location_list, all_location_object, map_manager.map_data)
    map_manager.update_map_data(map_data)

    print(f"更新後地圖資料 {map_manager.map_data}")
    print(f"目前地點 {character1.current_location}")
    print(f"人物記憶 {character1.memory_system.person_memory}")

    if interactive_character_name != "Nothing":
        print(f"互動角色 {interactive_character_name}")
        interactive_character  = character_dict[interactive_character_name]
        dialogue_history = character1.character_dialogue(interactive_character, map_manager.map_data, [])

if __name__ == "__main__":
    main()