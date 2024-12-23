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
        self.memory = MemorySystem(memory=character_data["memory"], capacity=100)
        self.current_location = character_data["current_location"]
        self.current_object = character_data["current_object"]
        self.name = character_data['personality']["name"]
    
        
    def character_action(self, map_data: Dict):
        """更新角色状态"""
        # 1. 环境感知
        map_information = {
            "observe": map_data[self.current_location]['observe'],
            "location_list": map_data[self.current_location]['location_list'],
            "all_location_object": map_data[self.current_location]['all_location_object'],
            "nearby_characters": map_data[self.current_location]['nearbyPersons']
        }

        # 2. 決策
        do_action = False
        temp_memory = ""
        while not do_action:
            action = self.decision.decision_action(memory, self.current_location, map_information, temp_memory)
            do_action, action_message = check_action_valid(action, map_data)
            if do_action == False:
                temp_memory += action["action"] + action_message
                time.sleep(1)
        
        # 3. 執行動作後更新角色狀態
        self.current_location = action["location"]
        if action['object'] != "Nothing":
            map_data[self.current_location][action['object']] -= 1
        if len(self.current_object) != 0 and self.current_object != "Nothing":
            map_data[self.current_location][self.current_object] += 1
        
        self.current_object = action['object']
        
        return map_data

class DecisionSystem:
    def __init__(self, personality: Dict, schedule: Dict):
        self.personality = personality
        self.current_schedule = schedule

    def init_schedule(self, person_memory: str) -> None:
        today_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A")
        self.current_schedule = schedule_create_method(self.personality, person_memory, today_time)['today_schedule']

    def decision_action(self, memory, current_location, map_information) -> Dict:
        """决策行动"""
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        action = design_action_method(
            self.personality,
            memory,
            self.current_schedule,
            map_information["observe"],
            current_location,
            current_time,
            map_information["location_list"],
            map_information["all_location_object"],
            map_information["nearby_characters"]
        )
        return action
        
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
        """管理记忆容量"""
        if len(self.person_memory) > self.capacity:
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