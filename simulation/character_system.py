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
        self.change_location_flag = False
        
    def character_action(self, location_list, all_location_object, all_map_data, event_content):
        """生成人物行動"""
        self.change_location_flag = False
        path = {}
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "location_list": location_list,
            "all_location_object": all_location_object,
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        # 1. 決策
        do_action = False
        temp_memory = event_content or ""

        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        while True:
            action = self.decision.decision_action(self.memory_system.person_memory, self.current_location, current_time, map_information, temp_memory)
            do_action, action_message = check_action_valid(action, map_information['all_map_data'])
            # 如果動作無法執行，則將加入失敗原因到暫存記憶中，重新生成動作
            if do_action == False:
                break
            temp_memory += action["action"] + action_message
        
        debug_print(f"人物行動 - 第一步 生成動作\n{action}", '紫色')
        
        # 2. 執行動作後更新角色狀態
        action['location'] = action['location'] if action['location'] in location_list else "其他區域"
        if self.current_location != action['location']:
            self.change_location_flag = True
            path = {"source": self.current_location, "target": action['location']}
        
        map_information = self.update_character_location_to_map(action, map_information)
        self.memory_system.record_event("", current_time, action['action'], "[myself]")
        
        debug_print(f"人物行動 - 第二步 更新記憶\n{self.memory_system.person_memory}", '紅色')
        debug_print(f"更新地圖\n{map_information}", "綠色")

        return map_information["all_map_data"], action, self.change_location_flag, path

    def character_additional_action(self, all_map_data):
        """角色額外動作 包含保持現狀或開啟談話"""
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        additional_action = self.decision.additional_action(self.memory_system.person_memory, self.current_location, current_time, map_information)
        debug_print(f"人物額外動作\n{additional_action}", '紫色')
        
        if additional_action["addtion"] == "keep":
            return map_information["all_map_data"], None
        else:
            if additional_action["person"] not in map_information["nearby_characters"]:
                return map_information["all_map_data"], None
            action_content = "與"+additional_action['person']+"開啟對話"
            self.memory_system.record_event("", current_time, action_content, "[myself]")
            map_information["all_map_data"][self.current_location]['observe'].append({self.name: action_content})
            return map_information["all_map_data"], additional_action

    def character_thinking(self, all_map_data):
        """角色思考"""
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        think = self.decision.decision_thinking(self.memory_system.person_memory, self.current_location, current_time, map_information)
        self.memory_system.record_event("", current_time, think, "[myself_thinking]")
    
    def character_reaction(self, event_content, location_list, all_location_object, all_map_data):
        """角色反應 : 觀察到事件 從預設動作列表中選擇動作 [keep, new_action]"""
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "location_list": location_list,
            "all_location_object": all_location_object,
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        reaction = self.decision.decision_reaction(self.memory_system.person_memory, self.current_location, current_time, map_information, event_content)
        debug_print(f"人物反應\n{reaction}", '紫色')

        if reaction["reaction"] == "keep":
            return map_information["all_map_data"], None
        else:
            return map_information["all_map_data"], reaction
    
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
            debug_print(f"有改行程\n{self.decision.current_schedule}", '黃色')

    def character_reflection_personality(self):
        self.decision.personality_reflection(self.memory_system.person_memory)
        debug_print(f"個性改寫{self.decision.personality}", '藍色')

    def character_relationship_thinking(self, person_name):
        debug_print(f"目前社交關係{self.decision.personality}", '藍色')
        self.decision.character_relation_thinking(person_name, self.memory_system.person_memory)
        debug_print(f"社交關係更新{self.decision.personality}", '藍色')

    def update_character_location_to_map(self, action, map_data):
        """更新角色位置"""
        debug_print(map_data, "紅色")
        clean_map_information = self.clean_character_observe(copy.deepcopy(map_data))

        # 確保當前位置的 nearbyPersons 存在並移除角色
        current_location_data = clean_map_information['all_map_data'].get(self.current_location, {})
        nearby_persons = current_location_data.get('nearbyPersons', [])
        if self.name in nearby_persons:
            nearby_persons.remove(self.name)

        # 更新角色位置
        self.current_location = action['location']
        new_location_data = clean_map_information['all_map_data'].setdefault(self.current_location, {})
        new_location_data.setdefault('observe', []).append({self.name: action['action']})
        new_location_data.setdefault('nearbyPersons', []).append(self.name)

        # 更新物件狀態
        if action['object'] != "Nothing" and action["location"] != "其他區域":
            new_location_data[action['object']] = new_location_data.get(action['object'], 0) - 1
            self.current_object = action['object']
        if self.current_object and self.current_object != "Nothing":
            new_location_data[self.current_object] = new_location_data.get(self.current_object, 0) + 1

        return clean_map_information

    def clean_character_observe(self, map_data):
        """清除角色觀察"""
        map_information = copy.deepcopy(map_data)
        for location_data in map_information['all_map_data'].values():
            location_data['observe'] = [
                observe for observe in location_data.get('observe', [])
                if observe.get('name') != self.name
            ]
        return map_information

    def write_to_file(self, write_file_path, file_name):
        file_data = {
            "personality":self.decision.personality,
            "schedule":self.decision.current_schedule,
            "memory":self.memory_system.person_memory,
            "current_location":self.current_location,
            "current_object":self.current_object
        }
        with open(write_file_path+file_name, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, ensure_ascii=False)

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
        """附加行动 - 是否開始談話"""
        addition_action = check_additional_action_method(
            self.personality, 
            memory, 
            self.current_schedule, 
            map_information["observe"], 
            current_location, 
            current_time, 
            map_information["nearby_characters"])
        return addition_action
    
    def decision_reaction(self, memory, current_location, current_time, map_information, event_content) -> Dict:
        """决策反应"""
        reaction = reaction_method(
            self.personality,
            memory,
            self.current_schedule,
            map_information["observe"],
            current_location,
            current_time,
            map_information["location_list"],
            map_information["all_location_object"],
            map_information["nearby_characters"],
            event_content
        )
        return reaction

    def decision_thinking(self, memory, current_location, current_time,  map_information) -> str:
        """想法生成"""
        think = thinking_method(
            self.personality,
            memory,
            map_information["observe"],
            current_location,
            current_time
        )
        return think
    
    def check_need_adjust_schedule(self, memory, observe, current_time):
        """檢查是否需要調整日程"""
        check_flag = check_need_adjust_schedule_method(self.personality, memory, self.current_schedule, observe, current_time)
        debug_print(check_flag, "紅色")
        if check_flag == "true":
            return True
        return False

    def adjust_schedule(self, memory, observe, current_time):
        """調整日程"""
        self.current_schedule = adjust_schedule_method(self.personality, memory, self.current_schedule, observe, current_time)

    def create_dialogue(self, memory, interactive_character, observe, current_location, current_time, dialogue_history):
        """開啟談話 一人一段交互"""
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
        personality_reflection_info = personality_reflection_method(self.personality, memory)
        self.personality.update({key: personality_reflection_info[key] 
                             for key in ["job_occupation", "interests", "personality", "character_description"]})

    def character_relation_thinking(self, relation_person, memory):
        """角色關係思考"""
        relationship = copy.deepcopy(self.personality["relationship"])
        personality_relation = character_relation_thinking_method(self.personality, relation_person.name, self.personality["relationship"].get(relation_person, ""), memory)
        
        # 清除原本的关系
        self.personality["relationship"] = [r for r in relationship if relation_person.name not in r]  # 移除与relation_person的关系
        # 添加新的关系
        self.personality["relationship"].append({relation_person.name: personality_relation})

class MemorySystem:
    def __init__(self, memory: str, capacity: int = 100):
        # self.short_term: List[Dict] = []  # 短期记忆
        self.long_term: List[Dict] = []   # 长期记忆
        self.person_memory = memory  # 人物记忆
        self.capacity = capacity
    
    def record_event(self, person_name:str, time: str, content: str, label: str):
        if person_name == "":
            self.person_memory += time+" "+label+content+"\n"
        else:
            self.person_memory += time+" "+label+person_name+content+"\n"
    
    def retrieve_relevant_memory(self, model, tokenizer, top_k: int = 3) -> str:
        """
        從記憶中檢索最相關的前k個記憶
        Args:
            memory (str): 原始記憶字符串
            model: 語言模型
            tokenizer: 分詞器
            top_k (int): 需要返回的記憶數量
        Returns:
            str: 篩選後的記憶字符串
        """
        try:
            # 如果記憶為空，直接返回空字符串
            if not self.person_memory:
                return ""
                
            # 如果記憶是字符串但不是JSON格式，直接返回
            if isinstance(self.person_memory, str) and not self.person_memory.strip().startswith("{"):
                return self.person_memory
                
            # 嘗試解析JSON
            memory_dict = json.loads(self.person_memory) if isinstance(self.person_memory, str) else self.person_memory
            
            # 如果記憶數量小於等於 top_k，直接返回原始記憶
            if len(memory_dict) <= top_k:
                return self.person_memory
                
            latest_time = max(memory_dict.keys())
            query = memory_dict[latest_time]
            
            # 為每條記憶評分
            scored_memories = []
            for time_stamp, memory_content in memory_dict.items():
                # 使用模型評估重要性和相關性
                prompt = f"""請評估以下記憶的重要性（1-10分）和與當前情境的相關性（1-10分）：
    當前情境：{query}
    待評估記憶：{memory_content}
    請只回傳兩個數字，用逗號分隔，例如：8,7"""
                
                response, _ = make_design(model, tokenizer, {}, prompt)
                try:
                    importance, relevance = map(int, response.strip().split(','))
                    score = (importance + relevance) / 20.0  # 正規化到 [0,1]
                    scored_memories.append((score, time_stamp, memory_content))
                except:
                    scored_memories.append((0, time_stamp, memory_content))
            
            # 排序並選擇前k個記憶
            scored_memories.sort(reverse=True)  # 按分數降序排序
            selected_memories = scored_memories[:top_k]
            
            # 創建新的記憶字典，保持時間順序
            selected_memories.sort(key=lambda x: x[1])  # 按時間戳排序
            result_dict = {time_stamp: content 
                        for _, time_stamp, content in selected_memories}
            
            return result_dict
        
        except Exception as e:
            print(f"Error in retrieve_relevant_memory: {e}")
            return ""
    
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
        """獲取地圖數據"""
        with open(write_file_path+"map_information.json", "r", encoding="utf-8") as f:
            self.map_data = json.load(f)

    def get_map_data(self, location: str) -> Dict:
        """獲取指定位置的地圖數據"""
        return self.map_data.get(location, {})
    
    def get_list_of_locations(self) -> List[str]:
        """獲取地圖中所有位置的列表, 
        return list of 地點"""
        return list(self.map_data.keys())

    def get_list_of_all_objects(self) -> Dict[str, List[str]]:
        """獲取地圖中所有物品的dict"""
        all_objects = {}
        for location, items in self.map_data.items():
            all_objects[location] = [key for key in items.keys() if key not in ["observe", "nearbyPersons"]]
        return all_objects

    def map_default_setting(self, character1, character2, character3):
        """將人物加進地圖資訊中"""
        for character in [character1, character2, character3]:
            if character.current_location in self.map_data:
                self.map_data[character.current_location]['nearbyPersons'].append(character.name)

    def update_map_data(self, map_data):
        self.map_data = map_data

    def write_to_file(self, write_file_path: str):
        """将地图数据写入文件"""
        with open(write_file_path+"map_information.json", "w", encoding="utf-8") as f:
            json.dump(self.map_data, f, ensure_ascii=False, indent=4)

# debug 用
import sys
def print_colored(text, color, end='\n'):
    colors = {
        '紅色': '\x1b[31m',
        '綠色': '\x1b[32m',
        '黃色': '\x1b[33m',
        '藍色': '\x1b[34m',
        '紫色': '\x1b[35m',
        '青色': '\x1b[36m'
    }
    reset = '\x1b[0m'
    sys.stdout.write(colors.get(color, '') + text + reset + end)

def debug_print(text, color):
    print_colored("-"*70, color)
    print(text)
    print_colored("-"*70, color)
