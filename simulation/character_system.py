from datetime import datetime
import json
from typing import Dict, List, Any

class CharacterManager:
    def __init__(self, character_data: Dict):
        self.perception = EnvironmentPerception()
        self.decision = DecisionSystem(
            character_data["personality"],
            character_data["schedule"]
        )
        self.executor = ActionExecutor()
        self.memory = MemorySystem()
    
    def update(self, map_data: Dict, character_location: str):
        """更新角色状态"""
        # 1. 环境感知
        perception_result = self.perception.update(map_data, character_location)
        
        # 2. 决策过程
        situation = self.decision.evaluate_situation(perception_result)
        options = self.decision.generate_options(situation)
        selected_action = self.decision.select_action(options)
        
        # 3. 执行行动
        action_result = self.executor.execute_action(selected_action, map_data)
        
        # 4. 记录记忆
        self.memory.record_event({
            "action": selected_action,
            "result": action_result,
            "perception": perception_result
        })
        
        return action_result
        
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
        self.memory = []
        self.goals: List[str] = []
        self.action_weights = {
            "schedule_priority": 0.4,
            "personality_priority": 0.3,
            "environment_priority": 0.3
        }
    
    def evaluate_situation(self, perception: Dict) -> Dict:
        """评估当前情况"""
        current_time = perception["time"]
        schedule_action = self._check_schedule(current_time)
        environment_action = self._evaluate_environment(perception)
        personality_action = self._consider_personality(perception)
        
        return {
            "schedule_based": schedule_action,
            "environment_based": environment_action,
            "personality_based": personality_action
        }
    
    def generate_options(self, evaluation: Dict) -> List[Dict]:
        """生成可能的行动选项"""
        options = []
        for action_type, action in evaluation.items():
            weight = self.action_weights.get(action_type.split("_")[0] + "_priority", 0.2)
            options.append({
                "action": action,
                "weight": weight,
                "type": action_type
            })
        return options
    
    def select_action(self, options: List[Dict]) -> Dict:
        """选择最终行动"""
        # 根据权重选择行动
        selected_action = max(options, key=lambda x: x["weight"])
        return {
            "action": selected_action["action"],
            "reason": f"Based on {selected_action['type']}"
        }
    
    def _check_schedule(self, current_time: str) -> str:
        """检查当前时间表"""
        current_hour = datetime.strptime(current_time, "%Y-%m-%d %A %H:%M").hour
        for time_slot, activity in self.current_schedule.items():
            schedule_hour = int(time_slot.split(":")[0])
            if schedule_hour == current_hour:
                return activity
        return "空闲活动"
    
    def _evaluate_environment(self, perception: Dict) -> str:
        """评估环境因素"""
        if not perception["objects"] and not perception["characters"]:
            return "探索环境"
        
        if perception["characters"]:
            return "与他人互动"
            
        return "使用周围物品"
    
    def _consider_personality(self, perception: Dict) -> str:
        """考虑性格因素"""
        personality_type = self.personality.get("type", "neutral")
        if personality_type == "extrovert":
            return "寻找社交机会"
        elif personality_type == "introvert":
            return "独处活动"
        return "随机活动"

class ActionExecutor:
    def __init__(self):
        self.current_action: Dict = None
        self.action_status: str = "idle"
        self.action_results: List[Dict] = []
    
    def execute_action(self, action: Dict, map_data: Dict) -> Dict:
        """执行具体行动"""
        self.current_action = action
        self.action_status = "executing"
        
        # 执行行动并更新地图状态
        result = self._perform_action(action, map_data)
        
        self.action_status = "completed"
        self.action_results.append(result)
        
        return result
    
    def _perform_action(self, action: Dict, map_data: Dict) -> Dict:
        """实际执行行动的具体逻辑"""
        # 实现具体行动逻辑
        pass

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