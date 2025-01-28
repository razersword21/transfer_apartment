from model import *
from prompt_new import *
from method import *
from config_new import *
from action_method import *
from character_system import *
import logging
logging.basicConfig(level=logging.INFO)
import shutil

def default_setting():
    # 將在file_path中的json檔案複製到write_file_path 正式遊戲時不使用
    for file in os.listdir(file_path):
        shutil.copy(file_path+file, write_file_path+file)
    logging.info(" 資料初始化...")
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
    map_manager, character1, character2, character3= default_setting()
    debug_print(map_manager.map_data, "綠色")
    debug_print(character1.decision.personality, '藍色')
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

    character1.decision.init_schedule(character1.memory_system.person_memory)
    # character2.decision.init_schedule(character2.memory_system.person_memory)
    # character3.decision.init_schedule(character3.memory_system.person_memory)
    debug_print(f"{character1.name}的行程表: {character1.decision.current_schedule}", '黃色')

    location_list = map_manager.get_list_of_locations()
    all_location_object = map_manager.get_list_of_all_objects()
    debug_print(f"location_list\n{location_list}\nall_location_object\n{all_location_object}", "綠色")
    
    if len(character1.status) == 0: # while len(character1.status) == 0
        map_data, action, is_change_location, path = character1.character_action(location_list, all_location_object, map_manager.map_data, "")
        if is_change_location:
            current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
            other_character = [character_dict[person] for person in character_dict.keys() if person != character1.name]
            for character in other_character:
                if character.current_location == path["source"]:
                    character.memory_system.record_event(character1.name, current_time, "離開了"+path["source"], "[others]")
                elif character.current_location == path["target"]:
                    character.memory_system.record_event(character1.name, current_time, "來到了"+path["destination"]+"開始"+action['action'], "[others]")
                debug_print(f"當有人改變位置需要寫到其他人的記憶\n{character.memory_system.person_memory}", '青色')
        
        map_manager.update_map_data(map_data)
        debug_print(f"更新地圖\n{map_manager.map_data}", "綠色")

        additional_map_data, additional_action = character1.character_additional_action(map_manager.map_data)
        map_manager.update_map_data(additional_map_data)
        debug_print(f"更新地圖\n{map_manager.map_data}", "綠色")

        if additional_action != None:
            if additional_action["person"] != "Nothing" and additional_action["addtion"] == "start_dialogue":
                print_colored("-"*70, '青色')
                current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
                interactive_character  = character_dict[additional_action["person"]]
                interactive_character.memory_system.record_event(character1.name, current_time, "與你開啟對話", "[others]")
                
                start_person_stop_dialogue, interactive_person_stop_dialogue = False, False
                dialogue_history = []

                while(start_person_stop_dialogue == False and interactive_person_stop_dialogue == False):
                    dialogue_history, start_person_stop_dialogue = character1.character_dialogue(interactive_character, map_manager.map_data, dialogue_history)
                    print(f"對話歷史 {dialogue_history}")
                    dialogue_history, interactive_person_stop_dialogue = interactive_character.character_dialogue(character1, map_manager.map_data, dialogue_history)
                    print(f"對話歷史 {dialogue_history}")
                
                print_colored("-"*70, '青色')
                character1.status = ""
                interactive_character.status = ""

        character1.character_thinking(map_manager.map_data)
        debug_print(f"記憶添加想法\n{character1.memory_system.person_memory}", '紫色')
        character1.character_adjust_schedule(map_manager.map_data)
    
        # 測試反應
        event_content = "廚房瓦斯沒關有異味\n"
        map_data, reaction = character1.character_reaction(event_content, location_list, all_location_object, map_manager.map_data)
        if reaction != None:
            map_data, action, is_change_location, path = character1.character_action(location_list, all_location_object, map_manager.map_data, event_content)
            if is_change_location:
                current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
                other_character = [character_dict[person] for person in character_dict.keys() if person != character1.name]
                for character in other_character:
                    if character.current_location == path["source"]:
                        character.memory_system.record_event(character1.name, current_time, "離開了"+path["source"], "[others]")
                    elif character.current_location == path["target"]:
                        character.memory_system.record_event(character1.name, current_time, "來到了"+path["destination"]+"開始"+action['action'], "[others]")
                    debug_print(f"當有人改變位置需要寫到其他人的記憶\n{character.memory_system.person_memory}", '青色')
        
        map_manager.update_map_data(map_data)
        debug_print(f"更新地圖\n{map_manager.map_data}", "綠色")
        map_manager.update_map_data(map_data)
        debug_print(f"更新地圖\n{map_manager.map_data}", "綠色")

        # 反思內容
        character1.character_reflection_personality()
        relation_person_list = [character_dict[person] for person in character_dict.keys() if person != character1.name]
        for person in relation_person_list:
            character1.character_relationship_thinking(person.name)

if __name__ == "__main__":
    main()