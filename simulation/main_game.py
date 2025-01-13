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

    global_queue = QueueManager()

    return map_manager, character1, character2, character3,  global_queue

def main():
    map_manager, character1, character2, character3, global_queue = default_setting()
    character_dict = {
        character1.name: character1,
        character2.name: character2,
        character3.name: character3
    }
    character_file_name_dict = {
        character1.name: "p1_information.json",
        character2.name: "p2_information.json",
        character3.name: "p3_information.json"
    }

    # character1.decision.init_schedule(character1.memory.person_memory)
    # character2.decision.init_schedule(character2.memory.person_memory)
    # character3.decision.init_schedule(character3.memory.person_memory)
    # print(f"人物1行程表: {character1.decision.current_schedule}")

    print(f"Init map data {map_manager.map_data}")
    location_list = map_manager.get_list_of_locations()
    all_location_object = map_manager.get_list_of_all_objects()
    
    if len(character1.status) == 0: # while len(character1.status) == 0
        map_data, action, is_change_location, path = character1.character_action(location_list, all_location_object, map_manager.map_data)
        if is_change_location:
            current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
            other_character = [character_dict[person] for person in character_dict.keys() if person != character1.name]
            for character in other_character:
                if character.current_location == path["source"]:
                    character.memory_system.record_event(character1.name, current_time, "離開了"+path["source"], "[others]")
                elif character.current_location == path["target"]:
                    character.memory_system.record_event(character1.name, current_time, "來到了"+path["destination"]+"開始"+action['action'], "[others]")
        map_manager.update_map_data(map_data)

        additional_map_data, additional_action = character1.character_additional_action(map_manager.map_data)
        map_manager.update_map_data(additional_map_data)

        print(f"更新後地圖資料 {map_manager.map_data}")
        print(f"目前地點 {character1.current_location}")
        print(f"人物記憶 {character1.memory_system.person_memory}")

        if additional_action["person"] != "Nothing" and additional_action["addtion"] == "start_dialogue":
            print(f"互動角色 {action["person"]}")
            interactive_character  = character_dict[additional_action["person"]]
            start_person_stop_dialogue, interactive_person_stop_dialogue = False, False
            dialogue_history = []

            while(start_person_stop_dialogue == False and interactive_person_stop_dialogue == False):
                dialogue_history, start_person_stop_dialogue = character1.character_dialogue(interactive_character, map_manager.map_data, dialogue_history)
                print(f"對話歷史 {dialogue_history}")
                dialogue_history, start_person_stop_dialogue = interactive_character.character_dialogue(character1, map_manager.map_data, dialogue_history)
                print(f"對話歷史 {dialogue_history}")
            print(f"對話結束")
            character1.status = ""
            interactive_character.status = ""

        character1.character_thinking()
        character1.character_adjust_schedule(map_manager.map_data)

        # 還沒寫提示詞等內容
        event_content = ""
        map_data, action = character1.character_reaction(event_content, location_list, all_location_object, map_manager.map_data)
        map_manager.update_map_data(map_data)

        # 反思內容
        relation_person_list = [character_dict[person] for person in character_dict.keys() if person != character1.name]
        for person in relation_person_list:
            character1.character_relation_thinking(person.name)

if __name__ == "__main__":
    main()