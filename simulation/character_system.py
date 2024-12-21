from datetime import datetime
import json
from typing import Dict, List, Any
from action_method import *

class CharacterManager:
    def __init__(self, character_data: Dict):
        self.perception = EnvironmentPerception()
        self.decision = DecisionSystem(
            character_data["personality"],
            character_data["schedule"]
        )
        self.memory = MemorySystem(character_data["memory"])
    
    def character_action(self, map_data: Dict, character_location: str):
        """更新角色状态"""
        # 1. 环境感知
        perception_result = self.perception.update(map_data, character_location)
        
        # 2. 决策过程
        vaild_action_flag = False
        while(vaild_action_flag == False):
            selected_action = self.decision.decision_action(perception_result, self.memory, self.decision.current_schedule, map_data)
            vaild_action_flag = self.check_action_validity(selected_action, map_data)
        
        # 3. 执行行动
        action_result = self.executor.execute_action(selected_action, map_data)
        
        # 4. 记录记忆
        self.memory.record_event({
            "action": selected_action,
            "result": action_result,
            "perception": perception_result
        })
        
        return action_result

    def check_action_validity(self, action: Dict, map_info: Dict) -> bool:
        if action["location"] not in map_info:
            return True
        else:
            map_data = map_info[action["location"]]
            if action["object"] in map_data and map_data[action["object"]] > 0:
                return True
            else:
                return False
        
        
class EnvironmentPerception:
    def __init__(self):
        self.current_location: str = None
        self.surrounding_objects: Dict[str, int] = {}  # 物品名称和数量
        self.nearby_characters: List[str] = []  # 附近的角色
        self.time_info: str = None
        self.observe_history: List[str] = []  # 观察历史
    
    def update(self, map_data: Dict, character_location: str) -> Dict:
        """更新环境信息"""
        self.current_location = character_location
        self.time_info = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        
        if character_location in map_data:
            location_data = map_data[character_location]
            self.surrounding_objects = {
                k: v for k, v in location_data.items() 
                if k != "observe"
            }
            self.nearby_characters = [
                obs.split()[0] for obs in location_data.get("observe", [])
            ]
            self.observe_history = location_data.get("observe", [])
        
        return {
            "location": self.current_location,
            "objects": self.surrounding_objects,
            "characters": self.nearby_characters,
            "time": self.time_info,
            "observations": self.observe_history
        }

class DecisionSystem:
    def __init__(self, personality: Dict, schedule: Dict):
        self.personality = personality
        self.current_schedule = schedule
        
    def decision_action(self, perception_result: Dict, memory: str, schedule: Dict, map_info: Dict) -> Dict:
        action = design_action_method(
            self.personality, 
            memory,
            schedule
        )
        return action
        

class MemorySystem:
    def __init__(self, capacity: int = 100):
        self.short_term: List[Dict] = []  # 短期记忆
        self.long_term: List[Dict] = []   # 长期记忆
        self.emotional_memory: Dict[str, List[Dict]] = {}  # 情感记忆
        self.capacity = capacity
    
    def record_event(self, event: Dict):
        """记录事件"""
        # 添加时间戳
        event["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 记录到短期记忆
        self.short_term.append(event)
        
        # 如果有情感标记，记录到情感记忆
        if "emotion" in event:
            emotion = event["emotion"]
            if emotion not in self.emotional_memory:
                self.emotional_memory[emotion] = []
            self.emotional_memory[emotion].append(event)
        
        # 管理记忆容量
        self._manage_memory_capacity()
    
    def retrieve_relevant_memory(self, context: Dict) -> List[Dict]:
        """检索相关记忆"""
        relevant_memories = []
        
        # 基于上下文检索记忆
        keywords = context.get("keywords", [])
        location = context.get("location")
        time_range = context.get("time_range")
        
        # 实现记忆检索逻辑
        return relevant_memories
    
    def _manage_memory_capacity(self):
        """管理记忆容量"""
        if len(self.short_term) > self.capacity:
            # 将旧的短期记忆转移到长期记忆
            oldest_memory = self.short_term.pop(0)
            self.long_term.append(oldest_memory)
    
    def get_formatted_memory(self) -> str:
        """返回格式化的记忆字符串"""
        formatted_memory = ""
        for memory in self.short_term:
            formatted_memory += f"{memory['time']} {memory['label']}"
            if memory.get('person'):
                formatted_memory += memory['person']
            formatted_memory += f"{memory['content']}\n"
        return formatted_memory