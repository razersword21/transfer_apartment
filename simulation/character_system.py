from datetime import datetime
import json
from typing import Dict, List, Any
from action_method import *  # Contains methods for validating and performing actions
from method import *  # Contains utility methods for decision-making and personality reflection
from config_new import *  # Configuration data for the system

# Class managing individual character's state, actions, and interactions
class CharacterManager:
    def __init__(self, character_data: Dict):
        # Initialize decision system with personality and schedule
        self.decision = DecisionSystem(
            character_data["personality"],
            character_data["schedule"]
        )
        # Initialize memory system with initial memory and capacity
        self.memory_system = MemorySystem(memory=character_data["memory"], capacity=100)
        self.current_location = character_data["current_location"]  # Current location on the map
        self.current_object = character_data["current_object"]  # Currently interacted object
        self.name = character_data['personality']["name"]  # Character's name
        self.status = ""  # Status like "idle" or "dialogue"
        self.change_location_flag = False  # Flag to track if the character moved

    def character_action(self, location_list, all_location_object, all_map_data):
        """
        Determine and execute the character's next action based on personality and map state.
        :param location_list: List of all locations on the map.
        :param all_location_object: List of all objects available in locations.
        :param all_map_data: Complete map data including objects and characters.
        :return: Updated map information, action details, movement flag, and path.
        """
        self.change_location_flag = False  # Reset movement flag
        path = {}  # Initialize empty path (source to target)

        # Prepare map information for decision-making
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "location_list": location_list,
            "all_location_object": all_location_object,
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }

        # Decision-making loop: Keep trying until a valid action is found
        do_action = False
        temp_memory = ""  # Temporary memory for invalid action reasons
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")  # Current timestamp
        while not do_action:
            # Decide action using personality, memory, and map context
            action = self.decision.decision_action(self.memory_system.person_memory, self.current_location, current_time, map_information, temp_memory)
            # Validate the decided action
            do_action, action_message = check_action_valid(action, map_information['all_map_data'])
            if not do_action:
                temp_memory += action["action"] + action_message  # Log invalid action reason

        # If location changes, update the path and set movement flag
        if self.current_location != action['location']:
            self.change_location_flag = True
            path = {"source": self.current_location, "target": action['location']}

        # Update character location on the map
        map_information = self.update_character_location_to_map(action, map_information)
        
        # Record the performed action in memory
        self.memory_system.record_event("", current_time, action['action'], "[myself]")

        return map_information, action, self.change_location_flag, path

    def character_additional_action(self, all_map_data):
        """
        Perform additional actions like starting a conversation.
        :param all_map_data: Complete map data.
        :return: Updated map information and additional action details.
        """
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        additional_action = self.decision.additional_action(self.memory_system.person_memory, self.current_location, current_time, map_information)
        
        if additional_action == "keep":
            return map_information, None  # No additional action performed
        else:
            # Log interaction details and update map state
            action_content = "與" + additional_action['person'] + "開啟對話"
            self.memory_system.record_event("", current_time, action_content, "[myself]")
            map_information["all_map_data"][self.current_location]['observe'].append({self.name: action_content})
            return map_information, additional_action

    def character_thinking(self):
        """
        Perform introspection or decision-making process for the character.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        think = self.decision.decision_thinking(self.memory_system.person_memory, self.current_location, current_time)
        self.memory_system.record_event("", current_time, think, "[myself]")

    def character_reaction(self, event_content, location_list, all_location_object, all_map_data):
        """
        Handle character's reaction to observed events.
        :param event_content: Content of the observed event.
        :param location_list: List of all locations on the map.
        :param all_location_object: List of all objects available in locations.
        :param all_map_data: Complete map data including objects and characters.
        :return: Updated map information and reaction details.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        map_information = {
            "observe": all_map_data[self.current_location].get('observe', []),
            "location_list": location_list,
            "all_location_object": all_location_object,
            "nearby_characters": all_map_data[self.current_location].get('nearbyPersons', []),
            "all_map_data": all_map_data
        }
        reaction = self.decision.decision_reaction(self.memory_system.person_memory, self.current_location, current_time, map_information, event_content)
        
        if reaction == "keep":
            return map_information, None  # No reaction
        else:
            action_content = "因為" + event_content + "而生成新動作"
            self.memory_system.record_event("", current_time, action_content, "[myself]")
            map_information["all_map_data"][self.current_location]['observe'].append({self.name: action_content})
            return map_information, reaction

    def character_dialogue(self, interactive_character, map_data, dialogue_history):
        """
        Handle dialogue between this character and another.
        :param interactive_character: The other character involved in the dialogue.
        :param map_data: Current map data.
        :param dialogue_history: List of previous dialogues.
        :return: Updated dialogue history and flag indicating if the dialogue stopped.
        """
        self.status = "dialogue"  # Set character's status to dialogue
        observe = map_data[self.current_location].get('observe', [])  # Observed details
        current_time = datetime.now().strftime("%Y-%m-%d %A %H:%M")
        
        # Generate dialogue content
        dialogue_content = self.decision.create_dialogue(
            self.memory_system.person_memory, 
            interactive_character.name, 
            observe, 
            self.current_location, 
            current_time,
            dialogue_history
        )
        
        dialogue_history.append({self.name: dialogue_content})  # Add to dialogue history
        stop_dialogue = dialogue_content == "<stop_dialogue>"  # Check if dialogue ended
        return dialogue_history, stop_dialogue

    def update_character_location_to_map(self, action, map_data):
        """
        Update the character's location on the map after performing an action.
        :param action: The action performed, including target location and object.
        :param map_data: Current map state.
        :return: Updated map data.
        """
        map_information = copy.deepcopy(map_data)  # Avoid mutating original map data
        clean_map_information = self.clean_character_observe(map_information)  # Remove outdated observations
        
        # Log action at the current location
        clean_map_information["all_map_data"][self.current_location]['observe'].append({self.name: action['action']})
        
        # Update character's presence in locations
        clean_map_information['all_map_data'][self.current_location]['nearbyPersons'].remove(self.name)
        self.current_location = action['location']  # Update to new location
        clean_map_information['all_map_data'][self.current_location]['nearbyPersons'].append(self.name)

        # Update object interactions
        if action['object'] != "Nothing":
            clean_map_information['all_map_data'][self.current_location][action['object']] -= 1
        if len(self.current_object) != 0 and self.current_object != "Nothing":
            clean_map_information['all_map_data'][self.current_location][self.current_object] += 1
        self.current_object = action['object']

        return clean_map_information

    def clean_character_observe(self, map_data):
        """
        Clean outdated observations for the character from the map.
        :param map_data: Map data to clean.
        :return: Cleaned map data.
        """
        map_information = copy.deepcopy(map_data)
        for location, location_data in map_information['all_map_data'].items():
            # Remove observations related to the character
            location_data['observe'] = [
                observe for observe in location_data['observe'] 
                if observe.get('name') != self.name
            ]
        return map_information

# Class for decision-making based on personality and context
class DecisionSystem:
    def __init__(self, personality: Dict, schedule: Dict):
        self.personality = personality  # Character's personality traits
        self.current_schedule = schedule  # Current schedule of the character

    def decision_action(self, memory, current_location, current_time, map_information, temp_memory) -> Dict:
        """
        Decide the next action for the character.
        :param memory: Character's memory.
        :param current_location: Current location of the character.
        :param current_time: Current timestamp.
        :param map_information: Environmental data (objects, nearby characters, etc.).
        :param temp_memory: Temporary memory of invalid actions.
        :return: Action details as a dictionary.
        """
        return design_action_method(
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

    def decision_reaction(self, memory, current_location, current_time, map_information, event_content) -> Dict:
        """
        Decide how the character reacts to an event.
        :param memory: Character's memory.
        :param current_location: Current location of the character.
        :param current_time: Current timestamp.
        :param map_information: Environmental data.
        :param event_content: Content of the observed event.
        :return: Reaction details as a dictionary.
        """
        return reaction_method(
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

    def create_dialogue(self, memory, interactive_character, observe, current_location, current_time, dialogue_history):
        """
        Create dialogue content for an interaction.
        :param memory: Character's memory.
        :param interactive_character: Name of the character to interact with.
        :param observe: Current observations.
        :param current_location: Current location of the character.
        :param current_time: Current timestamp.
        :param dialogue_history: History of previous dialogues.
        :return: Generated dialogue content.
        """
        return create_dialogue_method(
            self.personality,
            interactive_character,
            memory,
            observe,
            current_location,
            current_time,
            dialogue_history
        )

# Class managing character's memory systems
class MemorySystem:
    def __init__(self, memory: str, capacity: int = 100):
        self.long_term: List[Dict] = []   # Long-term memory storage
        self.person_memory = memory  # Current memory of the character
        self.capacity = capacity  # Maximum capacity for memory

    def record_event(self, person_name: str, time: str, content: str, label: str):
        """
        Record an event in the character's memory.
        :param person_name: Name of the person involved in the event.
        :param time: Timestamp of the event.
        :param content: Content of the event.
        :param label: Label for the event (e.g., [myself], [interaction]).
        """
        if person_name == "":
            self.person_memory += time + " " + label + content + "\n"
        else:
            self.person_memory += time + " " + label + person_name + content + "\n"
        self._manage_memory_capacity()

    def _manage_memory_capacity(self):
        """
        Ensure memory does not exceed capacity. Move older memories to long-term storage if necessary.
        """
        memory_lines = self.person_memory.split("\n")
        if len(memory_lines) > self.capacity:
            oldest_memory = memory_lines.pop(0)  # Remove oldest memory
            self.long_term.append(oldest_memory)  # Add it to long-term storage
            self.person_memory = "\n".join(memory_lines)

# Class managing the map and its data
class MapManager:
    def __init__(self):
        self.map_data: Dict[str, Dict] = {}  # Stores map data as a dictionary

    def load_map(self, write_file_path: str):
        """
        Load map data from a JSON file.
        :param write_file_path: Path to the map data file.
        """
        with open(write_file_path + "map_information.json", "r", encoding="utf-8") as f:
            self.map_data = json.load(f)

    def get_map_data(self, location: str) -> Dict:
        """
        Get data for a specific location on the map.
        :param location: Location name.
        :return: Data for the specified location.
        """
        return self.map_data.get(location, {})

    def update_map_data(self, map_data):
        """
        Update the current map data.
        :param map_data: New map data to update.
        """
        self.map_data = map_data

    def write_to_file(self, write_file_path: str):
        """
        Save the current map data to a JSON file.
        :param write_file_path: Path to save the file.
        """
        with open(write_file_path + "map_information.json", "w", encoding="utf-8") as f:
            json.dump(self.map_data, f, ensure_ascii=False, indent=4)
