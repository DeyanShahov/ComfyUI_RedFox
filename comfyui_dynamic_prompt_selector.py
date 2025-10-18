import random
import time
import json
import os

# --- State Persistence ---

# Get the directory of the current script to store the state file alongside it
current_dir = os.path.dirname(os.path.realpath(__file__))
STATE_FILE = os.path.join(current_dir, "dynamic_prompt_selector.state.json")

def save_all_states(states):
    """Saves the current state to a JSON file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(states, f, indent=4)

def load_all_states():
    """Loads the state from a JSON file if it exists."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {} # Return an empty dict if the file doesn't exist

# --- Node Class ---

class DynamicPromptSelector:
    # This dictionary will hold the state for each node instance, identified by node_id.

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Base node_id for state management
                "node_id_base": ("STRING", {"default": "default"}),
                # Tab 1
                "prompt_text_tab1": ("STRING", {"multiline": True}),
                "delimiter_tab1": ("STRING", {"default": "|"}),
                "behavior_tab1": (["fix", "increment", "decrement", "random", "ping-pong"],),
                "start_index_tab1": ("INT", {"default": 0, "min": 0}),
                # Tab 2
                "prompt_text_tab2": ("STRING", {"multiline": True}),
                "delimiter_tab2": ("STRING", {"default": "|"}),
                "behavior_tab2": (["fix", "increment", "decrement", "random", "ping-pong"],),
                "start_index_tab2": ("INT", {"default": 0, "min": 0}),
                # Tab 3
                "prompt_text_tab3": ("STRING", {"multiline": True}),
                "delimiter_tab3": ("STRING", {"default": "|"}),
                "behavior_tab3": (["fix", "increment", "decrement", "random", "ping-pong"],),
                "start_index_tab3": ("INT", {"default": 0, "min": 0}),
                # Tab 4
                "prompt_text_tab4": ("STRING", {"multiline": True}),
                "delimiter_tab4": ("STRING", {"default": "|"}),
                "behavior_tab4": (["fix", "increment", "decrement", "random", "ping-pong"],),
                "start_index_tab4": ("INT", {"default": 0, "min": 0}),
                # Tab 5
                "prompt_text_tab5": ("STRING", {"multiline": True}),
                "delimiter_tab5": ("STRING", {"default": "|"}),
                "behavior_tab5": (["fix", "increment", "decrement", "random", "ping-pong"],),
                "start_index_tab5": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING", "INT", "INT", "STRING", "INT", "INT", "STRING", "INT", "INT", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("Tab1_Prompt", "Tab1_Index", "Tab1_Total", "Tab2_Prompt", "Tab2_Index", "Tab2_Total", "Tab3_Prompt", "Tab3_Index", "Tab3_Total", "Tab4_Prompt", "Tab4_Index", "Tab4_Total", "Tab5_Prompt", "Tab5_Index", "Tab5_Total", "Combined_Prompts")

    FUNCTION = "select_prompt_part"
    CATEGORY = "Custom/Dynamic"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """
        This method is used by ComfyUI to determine if the node's output has changed.
        By returning the current time, we force the node to re-evaluate every time.
        """
        return time.time()

    def _select_for_tab(self, prompt_text: str, delimiter: str, behavior: str, start_index: int, node_id: str):
        cls = self.__class__

        # Get the state for this specific node_id
        node_state = cls.NODE_STATES.get(node_id, {})

        current_index = node_state.get("current_index", start_index)

        parts = [p.strip() for p in prompt_text.split(delimiter) if p.strip()]
        if not parts:
            return ("", 0, 0)

        # If the prompt text has changed, reset the state
        if node_state.get("collection") != parts:
            node_state["collection"] = parts
            node_state["initialized"] = False

        collection = node_state.get("collection", parts)
        length = len(collection)

        # Clamp start_index to be within the valid range
        if start_index >= length:
            start_index = length - 1
        elif start_index < 0:
            start_index = 0

        # Initialize only on the first run or when the prompt changes
        if not node_state.get("initialized", False):
            current_index = start_index
            node_state["initialized"] = True

        # --- LOGIC ---
        if behavior == "fix":
            current_run_index = start_index
            current_index = start_index
        elif behavior == "random":
            current_run_index = random.randint(0, length - 1)
            current_index = current_run_index
        else:
            current_run_index = current_index
            ping_pong_direction = node_state.get("ping_pong_direction", 1)

            if behavior == "increment":
                current_index = (current_index + 1) % length
            elif behavior == "decrement":
                current_index = (current_index - 1) % length
            elif behavior == "ping-pong" and length > 1:
                if current_index <= 0 and ping_pong_direction == -1:
                    ping_pong_direction = 1
                elif current_index >= length - 1 and ping_pong_direction == 1:
                    ping_pong_direction = -1
                current_index += ping_pong_direction
            node_state["ping_pong_direction"] = ping_pong_direction

        current_part = collection[current_run_index]

        # Update the state for this node_id
        node_state["current_index"] = current_index
        cls.NODE_STATES[node_id] = node_state

        # Save all states to the file
        save_all_states(cls.NODE_STATES)

        return (current_part, current_run_index, length)

    def select_prompt_part(self, node_id_base: str,
                           prompt_text_tab1: str, delimiter_tab1: str, behavior_tab1: str, start_index_tab1: int,
                           prompt_text_tab2: str, delimiter_tab2: str, behavior_tab2: str, start_index_tab2: int,
                           prompt_text_tab3: str, delimiter_tab3: str, behavior_tab3: str, start_index_tab3: int,
                           prompt_text_tab4: str, delimiter_tab4: str, behavior_tab4: str, start_index_tab4: int,
                           prompt_text_tab5: str, delimiter_tab5: str, behavior_tab5: str, start_index_tab5: int):

        # Generate unique node_ids for each tab based on base
        node_id_tab1 = f"{node_id_base}_tab1"
        node_id_tab2 = f"{node_id_base}_tab2"
        node_id_tab3 = f"{node_id_base}_tab3"
        node_id_tab4 = f"{node_id_base}_tab4"
        node_id_tab5 = f"{node_id_base}_tab5"

        # Compute results for each tab
        result_tab1 = self._select_for_tab(prompt_text_tab1, delimiter_tab1, behavior_tab1, start_index_tab1, node_id_tab1)
        result_tab2 = self._select_for_tab(prompt_text_tab2, delimiter_tab2, behavior_tab2, start_index_tab2, node_id_tab2)
        result_tab3 = self._select_for_tab(prompt_text_tab3, delimiter_tab3, behavior_tab3, start_index_tab3, node_id_tab3)
        result_tab4 = self._select_for_tab(prompt_text_tab4, delimiter_tab4, behavior_tab4, start_index_tab4, node_id_tab4)
        result_tab5 = self._select_for_tab(prompt_text_tab5, delimiter_tab5, behavior_tab5, start_index_tab5, node_id_tab5)

        # Combine non-empty prompt parts into a combined string (joined with space)
        all_prompts = [result_tab1[0], result_tab2[0], result_tab3[0], result_tab4[0], result_tab5[0]]
        combined_prompts = " ".join([p for p in all_prompts if p])

        # Combine results into a single tuple, adding combined_prompts at the end
        return result_tab1 + result_tab2 + result_tab3 + result_tab4 + result_tab5 + (combined_prompts,)

# --- Node Registration ---

# Load the saved state when the module is first loaded
DynamicPromptSelector.NODE_STATES = load_all_states()
print(f"[DynamicPromptSelector] Loaded {len(DynamicPromptSelector.NODE_STATES)} states from file.")

NODE_CLASS_MAPPINGS = {"DynamicPromptSelector": DynamicPromptSelector}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptSelector": "Dynamic Prompt Selector"}
