# Dynamic Prompt Selector for ComfyUI

A custom node for ComfyUI that allows you to dynamically select parts from large text prompts split by delimiters. The node supports 5 independent tabs (each like a mini-prompt selector), various selection behaviors, and persists state across ComfyUI restarts.

## Features

- **5 Independent Tabs**: Each tab can have its own prompt text, delimiter, behavior, and settings, allowing multiple prompt selections in one node.
- **Text Splitting**: Automatically splits text into parts using configurable delimiters.
- **Multiple Behaviors**: Supports fixed index, increment, decrement, random, and ping-pong selection modes per tab.
- **State Persistence**: Saves each tab's state to a JSON file so selections continue correctly after ComfyUI restart.
- **Multi-instance Support**: Each tab can have its own state based on the `node_id_base` setting.
- **15 Outputs**: Provides selected part, index, and total count for each of the 5 tabs.

## Nodes

### Dynamic Prompt Selector

Contains 5 independent tabbed selectors, each splitting text and selecting parts based on configured behavior.

#### Inputs

- **node_id_base** (STRING, default: "default"): Base state ID for this node. Tabs will get unique IDs like "{node_id_base}_tab1", etc.

For each tab (1-5):

- **prompt_text_tab[X]** (STRING, multiline): The full text prompt for this tab. Parts separated by delimiter.
- **delimiter_tab[X]** (STRING, default: "|"): Delimiter to split text for this tab.
- **behavior_tab[X]** (MENU): Selection mode for this tab:
  - `fix`: Always uses the start_index value
  - `increment`: Increases index by 1 each run (wraps around)
  - `decrement`: Decreases index by 1 each run (wraps around)
  - `random`: Selects random index each run
  - `ping-pong`: Goes back and forth between index 0 and max (for lists > 1 item)
- **start_index_tab[X]** (INT, default: 0, min: 0): Initial index for this tab

#### Outputs

For each tab (1-5):

- **Tab[X]_Prompt** (STRING): Selected text part from tab X
- **Tab[X]_Index** (INT): 0-based index of current part for tab X
- **Tab[X]_Total** (INT): Total number of parts for tab X

- **Combined_Prompts** (STRING): Combined string of all non-empty selected prompt parts from all tabs, joined with spaces (tab1 + tab2 + ... + tab5 if not empty)

## Installation

1. Place this folder in your ComfyUI `custom_nodes` directory
2. Restart ComfyUI
3. The node will appear in the "Custom/Dynamic" category in ComfyUI

## Usage

### Basic Example

1. Set `prompt_text` to: `portrait of a woman | landscape painting | abstract art | still life`
2. Set `delimiter` to: `|`
3. Set `behavior` to: `increment`
4. Set `start_index` to: `0`
5. Set `node_id` to: `my_selector`

Each time you run the workflow, it will output the next part in sequence.

### Ping-Pong Behavior

With 3 parts: A|B|C
- Run 1: A (index 0)
- Run 2: B (index 1)
- Run 3: C (index 2)
- Run 4: B (index 1)
- Run 5: A (index 0)
- etc.

### Random Behavior

Selects a random part each run, saving the choice for consistency in that run.

### State Persistence

The node automatically saves each tab's state (current index, direction, etc.) to `dynamic_prompt_selector.state.json` in the same directory. This allows workflows to maintain state across ComfyUI restarts.

Each tab gets a unique automatic ID based on `node_id_base` (e.g., "default_tab1"). For multiple node instances, use different `node_id_base` values to avoid state conflicts. All states are stored in a single JSON file per node type.

## Notes

- If the prompt text changes, the node resets to the start_index
- Empty parts (after stripping whitespace) are ignored
- Behavior changes take effect immediately
- The state file is created automatically when first used

## Dependencies

This node requires no external Python packages - it uses only the standard library.

## License

[Specify license if applicable]
