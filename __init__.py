import random
import re
import time
import itertools

class M_RandomPromptSelector:
    """
    ComfyUI Node for random selection from a prompt in the {A|B|C} format.
    Includes options for random selection, cycling through options, or completely freezing the node.
    """
    
    def __init__(self):
        # Initialize internal state for tracking
        self.last_seed = int(time.time() * 1000) % 0xffffffffffffffff
        self.combinations = []
        self.current_index = -1
        self.last_text_input = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "Photo of {red|blue} {ball|box} on table"}),
                "mode": (
                    [
                        "🎲 new random", 
                        "🔄 fix last seed (cycle text)", 
                        "✍️ custom seed (cycle text)",
                        "🛑 fix last seed and text"
                    ], 
                    {"default": "🎲 new random"}
                ),
                "custom_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "seed")
    FUNCTION = "process_text"
    CATEGORY = "M_nodes"

    @classmethod
    def IS_CHANGED(s, text, mode, custom_seed):
        if mode == "🛑 fix last seed and text":
            return text
        return float("NaN")

    def get_combinations(self, text):
        parts = re.split(r'\{([^{}]+)\}', text)
        lists = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                lists.append(part.split('|'))
            else:
                lists.append([part])
        
        combinations = ["".join(c) for c in itertools.product(*lists)]
        return combinations

    def process_text(self, text, mode, custom_seed):
        if text != self.last_text_input or not self.combinations:
            self.combinations = self.get_combinations(text)
            self.current_index = -1
            self.last_text_input = text

        if mode == "🛑 fix last seed and text":
            if self.current_index == -1:
                self.current_index = 0
            result = self.combinations[self.current_index]
            
        elif mode == "🎲 new random":
            self.last_seed = int(time.time() * 1000) % 0xffffffffffffffff
            result = random.choice(self.combinations)
            self.current_index = self.combinations.index(result)
            
        elif mode == "✍️ custom seed (cycle text)":
            self.last_seed = custom_seed
            self.current_index = (self.current_index + 1) % len(self.combinations)
            result = self.combinations[self.current_index]
            
        else: 
            self.current_index = (self.current_index + 1) % len(self.combinations)
            result = self.combinations[self.current_index]

        return (result, self.last_seed)


class M_Multi_Note:
    """
    ComfyUI Node for dynamic notes.
    Displays a toggle, Title, and Content. Additional fields are loaded dynamically via JS.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enable_1": ("BOOLEAN", {"default": True}),
                "title_1": ("STRING", {"default": "Title 1"}),
                "text_1": ("STRING", {"multiline": True, "default": ""}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "unique_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("combined_text",)
    FUNCTION = "process"
    CATEGORY = "M_nodes"

    def process(self, prompt=None, unique_id=None, **kwargs):
        raw_inputs = kwargs.copy()
        if prompt is not None and unique_id is not None:
            raw_inputs.update(prompt[unique_id].get("inputs", {}))

        notes = []
        i = 1
        
        while True:
            enable_key = f"enable_{i}"
            text_key = f"text_{i}"
            
            if text_key in raw_inputs:
                is_enabled = raw_inputs.get(enable_key, True)
                if is_enabled:
                    text = raw_inputs.get(text_key, "")
                    if text.strip():  
                        notes.append(text.strip())
            else:
                break
            i += 1
            
        return (", ".join(notes),)


class M_Multi_Note_One_Select:
    """
    ComfyUI Node for dynamic notes.
    Exactly like M_Multi_Note, but acts like a radio button: only ONE note is processed.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enable_1": ("BOOLEAN", {"default": True}),
                "title_1": ("STRING", {"default": "Title 1"}),
                "text_1": ("STRING", {"multiline": True, "default": ""}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "unique_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_text",)
    FUNCTION = "process"
    CATEGORY = "M_nodes"

    def process(self, prompt=None, unique_id=None, **kwargs):
        raw_inputs = kwargs.copy()
        if prompt is not None and unique_id is not None:
            raw_inputs.update(prompt[unique_id].get("inputs", {}))

        i = 1
        while True:
            enable_key = f"enable_{i}"
            text_key = f"text_{i}"
            
            if text_key in raw_inputs:
                # Default to false for dynamically added ones if missing, except the first
                default_enable = True if i == 1 else False
                is_enabled = raw_inputs.get(enable_key, default_enable)
                
                # As soon as we find the FIRST enabled text, we return it instantly
                if is_enabled:
                    text = raw_inputs.get(text_key, "")
                    if text.strip():  
                        return (text.strip(),)
            else:
                break
            i += 1
            
        # Return empty string if nothing is enabled
        return ("",)


# Node registration mapping
NODE_CLASS_MAPPINGS = {
    "M_RandomPromptSelector": M_RandomPromptSelector,
    "M_Multi_Note": M_Multi_Note,
    "M_Multi_Note_One_Select": M_Multi_Note_One_Select
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "M_RandomPromptSelector": "Random Prompt {A|B|C} Selector",
    "M_Multi_Note": "Multi Note (Combine All)",
    "M_Multi_Note_One_Select": "Multi Note (One Select)"
}

WEB_DIRECTORY = "./js"