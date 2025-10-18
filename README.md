# Dynamic Prompt Selector for ComfyUI

A custom node for ComfyUI that allows you to dynamically select parts from a large text prompt split by delimiters. The node supports various selection behaviors and persists its state across ComfyUI restarts.

## Features

- **Text Splitting**: Automatically splits large prompt text into parts using a configurable delimiter.
- **Multiple Behaviors**: Supports fixed index, increment, decrement, random, and ping-pong selection modes.
- **State Persistence**: Saves node state to a JSON file so selections continue correctly after ComfyUI restart.
- **Multi-instance Support**: Each node instance can have its own state using the `node_id` parameter.
- **Dynamic Outputs**: Provides the current selected part, index, and total count.

## Nodes

### Dynamic Prompt Selector

Splits a multiline text prompt into parts and selects one based on the chosen behavior.

#### Inputs

- **prompt_text** (STRING, multiline): The full text prompt to split. Parts are separated by the delimiter.
- **delimiter** (STRING, default: "|"): The character or string used to split the prompt into parts.
- **behavior** (MENU): Selection mode:
  - `fix`: Always uses the start_index value
  - `increment`: Increases index by 1 each run (wraps around)
  - `decrement`: Decreases index by 1 each run (wraps around)
  - `random`: Selects random index each run
  - `ping-pong`: Goes back and forth between index 0 and max (for lists > 1 item)
- **start_index** (INT, default: 0, min: 0): Initial index to use when behavior allows
- **node_id** (STRING, default: "default"): Unique identifier for saving/loading state. Use different IDs for multiple instances.

#### Outputs

- **current_prompt_part** (STRING): The selected text part from the split prompt
- **current_index** (INT): The 0-based index of the current part
- **total_parts** (INT): Total number of parts in the split text

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

The node automatically saves its state (current index, direction, etc.) to `dynamic_prompt_selector.state.json` in the same directory. This allows workflows to maintain state across ComfyUI restarts.

Each `node_id` has its own saved state, so you can have multiple selectors with different behaviors running independently.

## Notes

- If the prompt text changes, the node resets to the start_index
- Empty parts (after stripping whitespace) are ignored
- Behavior changes take effect immediately
- The state file is created automatically when first used

## Dependencies

This node requires no external Python packages - it uses only the standard library.

## License

[Specify license if applicable]
