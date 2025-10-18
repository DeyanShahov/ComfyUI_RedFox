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
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Return empty dict if file is corrupted
    return {} # Return an empty dict if the file doesn't exist

# --- Node Class ---

class DynamicPromptSelector:
    NODE_STATES = {}

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "node_id_base": ("STRING", {"default": "default"}),
                # Tab 1
                "prompt_text_tab1": ("STRING", {"multiline": True, "default": ""}),
                "delimiter_tab1": ("STRING", {"default": "|"}),
                "behavior_tab1": (["fix", "increment", "decrement", "random", "ping-pong"], {"default": "fix"}),
                "start_index_tab1": ("INT", {"default": 0, "min": 0}),
                "batch_count_tab1": ("INT", {"default": 1, "min": 1, "max": 1024}),
                # Tab 2
                "prompt_text_tab2": ("STRING", {"multiline": True, "default": ""}),
                "delimiter_tab2": ("STRING", {"default": "|"}),
                "behavior_tab2": (["fix", "increment", "decrement", "random", "ping-pong"], {"default": "fix"}),
                "start_index_tab2": ("INT", {"default": 0, "min": 0}),
                "batch_count_tab2": ("INT", {"default": 1, "min": 1, "max": 1024}),
                # Tab 3
                "prompt_text_tab3": ("STRING", {"multiline": True, "default": ""}),
                "delimiter_tab3": ("STRING", {"default": "|"}),
                "behavior_tab3": (["fix", "increment", "decrement", "random", "ping-pong"], {"default": "fix"}),
                "start_index_tab3": ("INT", {"default": 0, "min": 0}),
                "batch_count_tab3": ("INT", {"default": 1, "min": 1, "max": 1024}),
                # Tab 4
                "prompt_text_tab4": ("STRING", {"multiline": True, "default": ""}),
                "delimiter_tab4": ("STRING", {"default": "|"}),
                "behavior_tab4": (["fix", "increment", "decrement", "random", "ping-pong"], {"default": "fix"}),
                "start_index_tab4": ("INT", {"default": 0, "min": 0}),
                "batch_count_tab4": ("INT", {"default": 1, "min": 1, "max": 1024}),
                # Tab 5
                "prompt_text_tab5": ("STRING", {"multiline": True, "default": ""}),
                "delimiter_tab5": ("STRING", {"default": "|"}),
                "behavior_tab5": (["fix", "increment", "decrement", "random", "ping-pong"], {"default": "fix"}),
                "start_index_tab5": ("INT", {"default": 0, "min": 0}),
                "batch_count_tab5": ("INT", {"default": 1, "min": 1, "max": 1024}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING", "INT", "INT", "STRING", "INT", "INT", "STRING", "INT", "INT", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("Tab1_Prompt", "Tab1_Index", "Tab1_Total", "Tab2_Prompt", "Tab2_Index", "Tab2_Total", "Tab3_Prompt", "Tab3_Index", "Tab3_Total", "Tab4_Prompt", "Tab4_Index", "Tab4_Total", "Tab5_Prompt", "Tab5_Index", "Tab5_Total", "Combined_Prompts")

    FUNCTION = "select_prompt_part"
    CATEGORY = "Custom/Dynamic"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return time.time()

    def _select_for_tab(self, prompt_text: str, delimiter: str, behavior: str, start_index: int, node_id: str):
        cls = self.__class__
        node_state = cls.NODE_STATES.get(node_id, {})
        
        parts = [p.strip() for p in prompt_text.split(delimiter) if p.strip()]
        if not parts:
            return ("", 0, 0)

        collection = parts
        length = len(collection)

        # Reset state if the collection has changed
        if node_state.get("collection") != collection:
            node_state["collection"] = collection
            node_state["initialized"] = False
            node_state["current_index"] = start_index

        # Clamp start_index to be within the valid range
        start_index = max(0, min(length - 1, start_index))

        # Initialize state on first run or after reset
        if not node_state.get("initialized", False):
            node_state["current_index"] = start_index
            node_state["initialized"] = True
            node_state["ping_pong_direction"] = 1

        current_index = node_state.get("current_index", start_index)
        ping_pong_direction = node_state.get("ping_pong_direction", 1)

        # Determine the index to use for this run
        run_index = current_index
        if behavior == "fix":
            run_index = start_index
        elif behavior == "random":
            run_index = random.randint(0, length - 1)
        
        # Clamp run_index to be safe
        run_index = max(0, min(length - 1, run_index))
        current_part = collection[run_index]

        # Determine the index for the *next* run
        next_index = run_index
        if behavior == "increment":
            next_index = (run_index + 1) % length
        elif behavior == "decrement":
            next_index = (run_index - 1 + length) % length
        elif behavior == "ping-pong" and length > 1:
            if run_index <= 0 and ping_pong_direction == -1:
                ping_pong_direction = 1
            elif run_index >= length - 1 and ping_pong_direction == 1:
                ping_pong_direction = -1
            next_index = run_index + ping_pong_direction
        elif behavior == "random":
             next_index = random.randint(0, length - 1) # next is also random
        elif behavior == "fix":
             next_index = start_index # next is also fixed

        # Update state for the next run
        node_state["current_index"] = next_index
        node_state["ping_pong_direction"] = ping_pong_direction
        cls.NODE_STATES[node_id] = node_state

        return (current_part, run_index, length)

    def select_prompt_part(self, node_id_base: str,
                           prompt_text_tab1: str, delimiter_tab1: str, behavior_tab1: str, start_index_tab1: int, batch_count_tab1: int,
                           prompt_text_tab2: str, delimiter_tab2: str, behavior_tab2: str, start_index_tab2: int, batch_count_tab2: int,
                           prompt_text_tab3: str, delimiter_tab3: str, behavior_tab3: str, start_index_tab3: int, batch_count_tab3: int,
                           prompt_text_tab4: str, delimiter_tab4: str, behavior_tab4: str, start_index_tab4: int, batch_count_tab4: int,
                           prompt_text_tab5: str, delimiter_tab5: str, behavior_tab5: str, start_index_tab5: int, batch_count_tab5: int):

        # Calculate total number of repetitions
        total_reps = batch_count_tab1 * batch_count_tab2 * batch_count_tab3 * batch_count_tab4 * batch_count_tab5

        # --- Get the single result for each tab ---
        tabs_params = [
            (prompt_text_tab1, delimiter_tab1, behavior_tab1, start_index_tab1, f"{node_id_base}_tab1"),
            (prompt_text_tab2, delimiter_tab2, behavior_tab2, start_index_tab2, f"{node_id_base}_tab2"),
            (prompt_text_tab3, delimiter_tab3, behavior_tab3, start_index_tab3, f"{node_id_base}_tab3"),
            (prompt_text_tab4, delimiter_tab4, behavior_tab4, start_index_tab4, f"{node_id_base}_tab4"),
            (prompt_text_tab5, delimiter_tab5, behavior_tab5, start_index_tab5, f"{node_id_base}_tab5"),
        ]
        
        single_results = [self._select_for_tab(*params) for params in tabs_params]

        # --- Assemble the single combined prompt ---
        prompts_to_combine = [res[0] for res in single_results if res and res[0]]
        combined_prompt_str = " ".join(prompts_to_combine)

        # --- Create output lists by repeating the single result ---
        output_lists = []
        for res in single_results:
            prompt, index, total = res
            output_lists.append([prompt] * total_reps)
            output_lists.append([index] * total_reps)
            output_lists.append([total] * total_reps)
        
        output_lists.append([combined_prompt_str] * total_reps)

        # Save all states once at the end of the run
        save_all_states(self.__class__.NODE_STATES)

        return tuple(output_lists)

# --- Node Registration ---

# Load the saved state when the module is first loaded
DynamicPromptSelector.NODE_STATES = load_all_states()
print(f"[DynamicPromptSelector] Loaded {len(DynamicPromptSelector.NODE_STATES)} states from file.")

NODE_CLASS_MAPPINGS = {"DynamicPromptSelector": DynamicPromptSelector}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptSelector": "Dynamic Prompt Selector"}

# --- Auto-Update Logic ---
import subprocess

def check_for_updates():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    git_dir = os.path.join(script_dir, '.git')

    if not os.path.isdir(git_dir):
        print("[DynamicPromptSelector] Not a git repository. Skipping update check.")
        return

    try:
        print("[DynamicPromptSelector] Checking for updates...")

        # Fetch latest changes from remote
        subprocess.run(['git', 'fetch'], cwd=script_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if local is behind remote
        status_result = subprocess.run(['git', 'status', '-uno'], cwd=script_dir, check=True, capture_output=True, text=True)

        if 'Your branch is behind' in status_result.stdout:
            print("[DynamicPromptSelector] New version found. Updating...")
            pull_result = subprocess.run(['git', 'pull'], cwd=script_dir, check=True, capture_output=True, text=True)
            print(f"[DynamicPromptSelector] Update complete. Please restart ComfyUI.\n{pull_result.stdout}")
        else:
            print("[DynamicPromptSelector] Already up to date.")

    except subprocess.CalledProcessError as e:
        print(f"[DynamicPromptSelector] Error during update check: {e.stderr.decode('utf-8').strip() if e.stderr else 'Unknown error'}")
    except FileNotFoundError:
        print("[DynamicPromptSelector] 'git' command not found. Please ensure Git is installed and in your PATH.")
    except Exception as e:
        print(f"[DynamicPromptSelector] An unexpected error occurred: {e}")

# Run the check when the module is loaded
check_for_updates()