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
                "prompt_text": ("STRING", {"multiline": True}),
                "delimiter": ("STRING", {"default": "|"}),
                "behavior": (["fix", "increment", "decrement", "random", "ping-pong"],),
                "start_index": ("INT", {"default": 0, "min": 0}),
                "node_id": ("STRING", {"default": "default"}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("current_prompt_part", "current_index", "total_parts")

    FUNCTION = "select_prompt_part"
    CATEGORY = "Custom/Dynamic"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """
        This method is used by ComfyUI to determine if the node's output has changed.
        By returning the current time, we force the node to re-evaluate every time.
        """
        return time.time()

    def select_prompt_part(self, prompt_text: str, delimiter: str, behavior: str, start_index: int, node_id: str):
        cls = self.__class__
        
        # Get the state for this specific node_id
        node_state = cls.NODE_STATES.get(node_id, {})

        print(f"\n--- [DynamicPromptSelector] RUNNING (ID: {node_id}) ---")
        print(f"[DynamicPromptSelector] Behavior: {behavior}")
        
        current_index = node_state.get("current_index", start_index)

        parts = [p.strip() for p in prompt_text.split(delimiter) if p.strip()]
        if not parts:
            print(f"[DynamicPromptSelector] No parts found. Returning empty.")
            return ("", 0, 0)

        # If the prompt text has changed, reset the state
        if node_state.get("collection") != parts:
            print(f"[DynamicPromptSelector] Prompt text changed. Resetting state.")
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
            print(f"[DynamicPromptSelector] Initializing. Setting index to start_index: {start_index}")
            current_index = start_index
            node_state["initialized"] = True

        print(f"[DynamicPromptSelector] Index before operation: {current_index}")

        # --- LOGIC ---
        # 1. Determine the index for the CURRENT run.
        # 2. Update the class index for the NEXT run.

        if behavior == "fix":
            # 'fix' always uses the value from the 'start_index' input
            current_run_index = start_index
            current_index = start_index  # Also save it for the next run
        elif behavior == "random":
            # 'random' selects a new random index for the current run
            current_run_index = random.randint(0, length - 1)
            current_index = current_run_index  # Save it for the next run
        else:
            # 'increment', 'decrement', 'ping-pong' use the saved state
            current_run_index = current_index
            ping_pong_direction = node_state.get("ping_pong_direction", 1)

            if behavior == "increment":
                current_index = (current_index + 1) % length
            elif behavior == "decrement":
                current_index = (current_index - 1) % length
            elif behavior == "ping-pong" and length > 1:
                # Check if the next step would be out of bounds
                if current_index <= 0 and ping_pong_direction == -1:
                    ping_pong_direction = 1
                elif current_index >= length - 1 and ping_pong_direction == 1:
                    ping_pong_direction = -1
                current_index += ping_pong_direction
            node_state["ping_pong_direction"] = ping_pong_direction

        current_part = collection[current_run_index]
        print(f"[DynamicPromptSelector] Index for THIS run: {current_run_index} -> \"{current_part}\"")
        print(f"[DynamicPromptSelector] Index for NEXT run: {current_index}")
        print(f"--- [DynamicPromptSelector] FINISHED ---\n")
        
        # Update the state for this node_id
        node_state["current_index"] = current_index
        cls.NODE_STATES[node_id] = node_state

        # Save all states to the file
        save_all_states(cls.NODE_STATES)

        return (current_part, current_run_index, length)

# --- Node Registration ---

# Load the saved state when the module is first loaded
DynamicPromptSelector.NODE_STATES = load_all_states()
print(f"[DynamicPromptSelector] Loaded {len(DynamicPromptSelector.NODE_STATES)} states from file.")

NODE_CLASS_MAPPINGS = {"DynamicPromptSelector": DynamicPromptSelector}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptSelector": "Dynamic Prompt Selector"}