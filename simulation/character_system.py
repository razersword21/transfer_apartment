from datetime import datetime
import json
from typing import Dict, List, Any
from action_method import *
from method import *
from config_new import *

class CharacterManager:
    def __init__(self, character_data: Dict):
        self.decision = DecisionSystem(
            character_data["personality"],
            character_data["schedule"]
        )
        self.memory_system = MemorySystem(memory=character_data["memory"], capacity=100)
        self.current_location = character_data["current_location"]
        self.current_object = character_data["current_object"]
        self.name = character_data['personality']["name"]
        self.status = ""
        
    def character_action(self, location_list, all_location_object, all_map_data):
        """更新角色状态"""
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "location_list": location_list,
            "all_location_object": all_location_object,
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        # 1. 決策
        do_action = False
        temp_memory = ""
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        while not do_action:
            action = self.decision.decision_action(self.memory_system.person_memory, self.current_location, current_time, map_information, temp_memory)
            do_action, action_message = check_action_valid(action, map_information['all_map_data'])
            if do_action == False:
                temp_memory += action["action"] + action_message
                time.sleep(1)
        
        # 2. 執行動作後更新角色狀態
        map_information = self.update_character_location(action, map_information)
        self.memory_system.record_event(None, current_time, action['action'], "[myself]")

        return map_information, action

    def character_additional_action(self, all_map_data):
        """角色額外動作"""
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        additional_action = self.decision.additional_action(self.memory_system.person_memory, self.current_location, current_time, map_information)
        if additional_action == "keep":
            return map_information, None
        else:
            action_content = "與"+additional_action['person']+"開啟對話"
            self.memory_system.record_event(None, current_time, action_content, "[myself]")
            map_information["all_map_data"][self.current_location]['observe'].append({self.name: action_content})
            return map_information, additional_action

    def character_thinking(self):
        """角色思考"""
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        think = self.decision.decision_thinking(self.memory_system.person_memory, self.current_location, current_time)
        self.memory_system.record_event(None, current_time, think, "[myself]")
    
    def character_reaction(self, event_content, location_list, all_location_object, all_map_data):
        """角色反應 : 觀察到事件 從預設動作列表中選擇動作 [keep, new_action]"""
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "location_list": location_list,
            "all_location_object": all_location_object,
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        pass
    
    def character_dialogue(self, interactive_character, map_data, dialogue_history):
        """角色對話"""
        self.status = "dialogue"
        observe = map_data[self.current_location].get('observe', [])
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        dialogue_content = self.decision.create_dialogue(
            self.memory_system.person_memory, 
            interactive_character.name, 
            observe, 
            self.current_location, 
            current_time,
            dialogue_history
        )
        dialogue_history.append({self.name: dialogue_content})
        stop_dialogue = False
        if dialogue_content == "<stop_dialogue>":
            stop_dialogue = True
        return dialogue_history, stop_dialogue

    def character_adjust_schedule(self, all_map_data):
        """調整行程"""
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', [])
        }
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        if self.decision.check_need_adjust_schedule(self.memory_system.person_memory, map_information['observe'], current_time):
            self.decision.adjust_schedule(self.memory_system.person_memory, map_information['observe'], current_time)

    def character_reflection_personality(self, memory):
        self.decision.personality_reflection(memory)

    def character_relationship_thinking(self, person_name, memory):
        relationship = self.decision.character_relation_thinking(person_name, memory)

    def update_character_location(self, action, map_data):
        """更新角色位置"""
        map_information = copy.deepcopy(map_data)
        clean_map_information = self.clean_character_observe(map_information)
        clean_map_information["all_map_data"][self.current_location]['observe'].append({self.name: action['action']})
        clean_map_information['all_map_data'][self.current_location]['nearbyPersons'].remove(self.name)
        self.current_location = action['location']
        clean_map_information['all_map_data'][self.current_location]['nearbyPersons'].append(self.name)

        if action['object'] != "Nothing":
            clean_map_information['all_map_data'][self.current_location][action['object']] -= 1
        if len(self.current_object) != 0 and self.current_object != "Nothing":
            clean_map_information['all_map_data'][self.current_location][self.current_object] += 1
        self.current_object = action['object']

        return clean_map_information

    def clean_character_observe(self, map_data):
        """清除角色觀察"""
        map_information = copy.deepcopy(map_data)
        for location, location_data in map_information['all_map_data'].items():
            location_data['observe'] = [
                observe for observe in location_data['observe'] 
                if observe.get('name') != self.name
            ]
        return map_information

class DecisionSystem:
    def __init__(self, personality: Dict, schedule: Dict):
        self.personality = personality
        self.current_schedule = schedule

    def init_schedule(self, person_memory: str) -> None:
        today_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A")
        self.current_schedule = schedule_create_method(self.personality, person_memory, today_time)['today_schedule']

    def decision_action(self, memory, current_location, current_time, map_information, temp_memory) -> Dict:
        """决策行动"""
        action = design_action_method(
            self.personality,
            memory,
            temp_memory,
            self.current_schedule,
            map_information["observe"],
            current_location,
            current_time,
            map_information["location_list"],
            map_information["all_location_object"],
            map_information["nearby_characters"]
        )
        return action
    
    def additional_action(self, memory, current_location, current_time, map_information) -> Dict:
        """附加行动"""
        addition_action = check_additional_action_method(
            self.personality, 
            memory, 
            self.current_schedule, 
            map_information["observe"], 
            current_location, 
            current_time, 
            map_information["nearby_characters"])
        return addition_action

    def decision_thinking(self, memory, current_location, current_time) -> str:
        """决策思考"""
        think = design_thinking_method(
            self.personality,
            memory,
            map_information["observe"],
            current_location,
            current_time
        )
        return think
    
    def check_need_adjust_schedule(self, memory, observe, current_time):
        """检查是否需要调整日程"""
        return check_need_adjust_schedule_method(memory, self.current_schedule, observe, current_time)

    def adjust_schedule(self, memory, observe, current_time):
        """调整日程"""
        self.current_schedule = adjust_schedule_method(memory, self.current_schedule, observe, current_time)

    def create_dialogue(self, memory, interactive_character, observe, current_location, current_time, dialogue_history):
        """创建对话"""
        dialogue = create_dialogue_method(
            self.personality,
            interactive_character,
            memory,
            observe,
            current_location,
            current_time,
            dialogue_history
        )
        return dialogue

    def personality_reflection(self, memory):
        """性格反思"""
        self.personality = personality_reflection_method(self.personality, memory)

    def character_relation_thinking(self, relation_person, memory):
        """角色关系思考"""
        relationship = copy.deepcopy(self.personality["relationship"])
        personality_relation = character_relation_thinking_method(self.personality, relation_person.name, self.personality["relationship"].get(relation_person, ""), memory)
        
        # 清除原本的关系
        self.personality["relationship"] = [r for r in relationship if relation_person.name not in r]  # 移除与relation_person的关系
        
        self.personality["relationship"].append({relation_person.name: personality_relation})

class MemorySystem:
    def __init__(self, memory: str, capacity: int = 100):
        self.short_term: List[Dict] = []  # 短期记忆
        self.long_term: List[Dict] = []   # 长期记忆
        self.person_memory = memory  # 人物记忆
        self.capacity = capacity
    
    def record_event(self, person_name:str, time: str, content: str, label: str):
        if person_name is None:
            self.person_memory += time+" "+label+content+"\n"
        else:
            self.person_memory += time+" "+label+person_name+content+"\n"
        # 管理记忆容量
        self._manage_memory_capacity()
    
    def retrieve_relevant_memory(self, context: Dict) -> List[Dict]:
        pass
    
    def _manage_memory_capacity(self):
        """管理记忆容量 或 改成整理记忆"""
        if len(self.person_memory.split("\n")) > self.capacity:
            # 将旧的短期记忆转移到长期记忆
            oldest_memory = self.person_memory.pop(0)
            self.long_term.append(oldest_memory)


class MapManager:
    def __init__(self):
        self.map_data: Dict[str, Dict] = {}

    def load_map(self, write_file_path: str):
        """加载地图数据"""
        # 从文件或数据库加载地图数据
        with open(write_file_path+"map_information.json", "r", encoding="utf-8") as f:
            self.map_data = json.load(f)

    def get_map_data(self, location: str) -> Dict:
        """获取指定位置的地图数据"""
        return self.map_data.get(location, {})
    
    def get_list_of_locations(self) -> List[str]:
        """获取地图中所有位置的列表"""
        return list(self.map_data.keys())

    def get_list_of_all_objects(self) -> Dict[str, List[str]]:
        """获取地图中所有物品的列表"""
        all_objects = {}
        for location, items in self.map_data.items():
            all_objects[location] = [key for key in items.keys() if key not in ["observe", "nearbyPersons"]]
        return all_objects

    def map_default_setting(self, character1, character2, character3):
        for character in [character1, character2, character3]:
            if character.current_location in self.map_data:
                self.map_data[character.current_location]['nearbyPersons'].append(character.name)

    def update_map_data(self, map_data):
        self.map_data = map_data