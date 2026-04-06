import random
import re
import time
import itertools
import os
import json
import numpy as np
from PIL import Image
import folder_paths


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



class M_Save_JPG_Advanced:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "oMo_Project"}),
                "subfolder": ("STRING", {"default": "oMoStudio_Gallery"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "save_prompt": ("BOOLEAN", {"default": False}),
                "save_workflow": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "group_name_1": ("STRING", {"default": "Main Generation"}),
                "positive_1": ("STRING", {"forceInput": True}),
                "negative_1": ("STRING", {"forceInput": True}),
                "seed_1": ("INT", {"forceInput": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "M_nodes"

    def save_images(self, images, filename_prefix, subfolder, quality, save_prompt, save_workflow, prompt=None, extra_pnginfo=None, **kwargs):
        if len(images) == 0:
            return {"ui": {"images": []}}

        if subfolder.strip() != "":
            full_prefix = os.path.join(subfolder.strip(), filename_prefix).replace('\\', '/')
        else:
            full_prefix = filename_prefix

        full_output_folder, filename, counter, subfolder_out, filename_prefix = folder_paths.get_save_image_path(
            full_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )

        results = list()
        for image in images:
            # Convert tensor to numpy array and scale to 0-255
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # Convert to RGB to prevent Pillow saving errors (JPG doesn't support alpha channel)
            if img.mode != "RGB":
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert("RGB")

            file_name = f"{filename}_{counter:05}_.jpg"
            file_path = os.path.join(full_output_folder, file_name)
            base_name = os.path.splitext(file_name)[0]

            img.save(file_path, quality=quality, optimize=True)

            # --- EXTRACT METADATA (Readable Text - HYBRID) ---
            if save_prompt and prompt is not None:
                txt_path = os.path.join(full_output_folder, f"{base_name}.txt")
                txt_content = []

                # STEP 1: EXACT DATA FROM WIRES (Dynamic extraction)
                wired_groups = {}
                wired_pos = []
                wired_neg = []
                wired_seeds = []

                # Dynamically collect all group indices from kwargs using Regex
                # This removes the hardcoded limit and only processes connected groups
                for key in kwargs.keys():
                    match = re.search(r'(positive|negative|seed|group_name)_(\d+)$', key)
                    if match:
                        idx = int(match.group(2))
                        if idx not in wired_groups:
                            wired_groups[idx] = {"name": f"Group {idx}", "seed": None, "positive": None, "negative": None}

                # Populate the dynamic dictionary with actual data
                for idx, group in sorted(wired_groups.items()):
                    group["name"] = kwargs.get(f"group_name_{idx}", f"Group {idx}")
                    group["positive"] = kwargs.get(f"positive_{idx}")
                    group["negative"] = kwargs.get(f"negative_{idx}")
                    group["seed"] = kwargs.get(f"seed_{idx}")
                    
                    # Store existing values to prevent duplicates in automatic extraction
                    if group["positive"]: wired_pos.append(group["positive"])
                    if group["negative"]: wired_neg.append(group["negative"])
                    if group["seed"] is not None: wired_seeds.append(str(group["seed"]))

                # Format wired groups for TXT output
                if wired_groups:
                    for idx, group in sorted(wired_groups.items()):
                        # Only write the group if there is actual input data
                        if group['seed'] is not None or group['positive'] or group['negative']:
                            txt_content.append(f"=== {group['name'].upper()} ===")
                            if group['seed'] is not None: txt_content.append(f"Seed: {group['seed']}")
                            if group['positive']: txt_content.append(f"Positive Prompt:\n{group['positive']}\n")
                            if group['negative']: txt_content.append(f"Negative Prompt:\n{group['negative']}\n")
                            txt_content.append("") 

                # STEP 2: AUTOMATIC DETECTION (Fallback and missing data completion)
                seeds = []
                pos_prompts = []
                neg_prompts = []
                other_texts = []
                
                # Recursive text resolution with depth limit to prevent infinite loops
                def resolve_text(node_link, depth=0):
                    if depth > 5: return "" # Recursion safeguard

                    if isinstance(node_link, list) and len(node_link) > 0:
                        node_id = str(node_link[0])
                        if node_id in prompt:
                            node_inputs = prompt[node_id].get("inputs", {})
                            
                            # Explicitly target prompt keys to avoid capturing model names, etc.
                            for target_key in ["text", "text_g", "text_l", "prompt"]:
                                if target_key in node_inputs:
                                    val = node_inputs[target_key]
                                    if isinstance(val, str):
                                        return val
                                    elif isinstance(val, list):
                                        return resolve_text(val, depth + 1)
                                        
                    elif isinstance(node_link, str):
                        return node_link
                    return ""

                # Scan graph for Samplers to extract fallback seeds and prompts
                for node_id, node_info in prompt.items():
                    class_type = node_info.get("class_type", "")
                    inputs = node_info.get("inputs", {})
                    
                    if "Sampler" in class_type:
                        s = None
                        if "seed" in inputs: s = str(inputs["seed"])
                        elif "noise_seed" in inputs: s = str(inputs["noise_seed"])
                        
                        # Add Seed only if it wasn't already provided via wires
                        if s and s not in seeds and s not in wired_seeds:
                            seeds.append(s)
                        
                        # Add Prompts only if they weren't already provided via wires
                        if "positive" in inputs:
                            txt = resolve_text(inputs["positive"])
                            if txt and txt not in pos_prompts and txt not in wired_pos: 
                                pos_prompts.append(txt)
                                
                        if "negative" in inputs:
                            txt = resolve_text(inputs["negative"])
                            if txt and txt not in neg_prompts and txt not in wired_neg: 
                                neg_prompts.append(txt)

                # Scan graph for stray CLIPTextEncode nodes
                for node_id, node_info in prompt.items():
                    if node_info.get("class_type", "") == "CLIPTextEncode":
                        txt = resolve_text(node_id)
                        # Exclude strings already captured
                        if txt and txt not in pos_prompts and txt not in neg_prompts and txt not in other_texts and txt not in wired_pos and txt not in wired_neg:
                            other_texts.append(txt)

                # STEP 3: APPEND AUTO-EXTRACTED DATA TO FILE
                if seeds or pos_prompts or neg_prompts or other_texts:
                    txt_content.append("=== AUTO-EXTRACTED WORKFLOW DATA ===")
                    if seeds: txt_content.append(f"Seed: {', '.join(set(seeds))}\n")
                    if pos_prompts:
                        txt_content.append("--- POSITIVE ---")
                        txt_content.append("\n---\n".join(pos_prompts) + "\n")
                    if neg_prompts:
                        txt_content.append("--- NEGATIVE ---")
                        txt_content.append("\n---\n".join(neg_prompts) + "\n")
                    if other_texts:
                        txt_content.append("--- OTHER TEXTS ---")
                        txt_content.append("\n---\n".join(other_texts) + "\n")

                # Save the final text file
                if txt_content:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(txt_content).strip())

            # --- EXTRACT WORKFLOW (JSON) ---
            if save_workflow and extra_pnginfo is not None and "workflow" in extra_pnginfo:
                json_path = os.path.join(full_output_folder, f"{base_name}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(extra_pnginfo["workflow"], f, indent=4)

            # Register saved image to UI
            results.append({
                "filename": file_name,
                "subfolder": subfolder_out,
                "type": self.type
            })
            counter += 1

        return {"ui": {"images": results}}

# Node registration mapping
NODE_CLASS_MAPPINGS = {
    "M_RandomPromptSelector": M_RandomPromptSelector,
    "M_Multi_Note": M_Multi_Note,
    "M_Multi_Note_One_Select": M_Multi_Note_One_Select,
    "M_Save_JPG_Advanced": M_Save_JPG_Advanced
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "M_RandomPromptSelector": "Random Prompt {A|B|C} Selector",
    "M_Multi_Note": "Multi Note (Combine All)",
    "M_Multi_Note_One_Select": "Multi Note (One Select)",
    "M_Save_JPG_Advanced": "Save JPG Advanced"
}

WEB_DIRECTORY = "./js"