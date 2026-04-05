# ComfyUI-M-Nodes
Dynamic notes and randomized prompt selection for ComfyUI.

# M-Nodes for ComfyUI 🚀

A collection of utility nodes designed to streamline complex prompt engineering, dynamic note-taking, and randomized selection within ComfyUI.

## Features

### 1\. 🎲 Random Prompt {A|B|C} Selector

A powerful string manipulator that handles randomized selections.

  - **Syntax:** Use `{option A|option B|option C}` within your text.
  - **Modes:**
      - **🎲 New Random:** Generates a new seed and a new random string every execution.
      - **🔄 Fix Last Seed (Cycle):** Keeps the seed locked but cycles through all possible text combinations.
      - **✍️ Custom Seed:** Uses a manual seed to determine the selection.
      - **🛑 Fix Last Seed and Text:** Completely freezes the node (0.00s cache) to prevent any changes.

### 2\. 📝 Multi Note (Combine All)

A dynamic note-taking node that grows as you type.

  - **Dynamic UI:** Whenever you type into the last available "Content" block, a new set (Toggle, Title, Content) is automatically generated.
  - **Toggle Control:** Each note has a switch to include or exclude it from the final output.
  - **Smart Formatting:** Combines all active notes into a single string, separated by commas—perfect for building long prompts.
  - **Layout Preservation:** Remembers your custom node width even when adding new fields.

### 3\. 🔘 Multi Note (One Select)

Similar to the "Combine All" node, but functions like a **Radio Button** group.

  - **Exclusive Selection:** Enabling one note automatically disables all others in the node.
  - **Use Case:** Perfect for testing different art styles or lighting setups without deleting your previous ideas.

-----

## 🛠 Installation

1.  Open your terminal and navigate to the ComfyUI `custom_nodes` folder:
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Restart ComfyUI.

-----

## 💎 Technical Highlights

  - **Persistence Pro:** Unlike many dynamic nodes, M-Nodes correctly save and restore all fields when:
      - Switching browser tabs.
      - Refreshing the page.
      - Loading a workflow from a saved PNG/JSON.
  - **Bypassing Limitations:** Uses advanced internal mapping to ensure that dynamically created fields are correctly sent to the Python backend, overcoming the standard LiteGraph limitations.
  - **Non-Intrusive:** Respects user-defined node widths during dynamic expansion.

-----

## 📖 How to Use

### The "Master Prompt" Workflow

1.  Add a **Multi Note (Combine All)** node. Create separate blocks for `Subject`, `Pose`, `Environment`, and `Style`.
2.  Right-click the **Random Prompt Selector** and choose `Convert text to input`.
3.  Connect the `combined_text` output from the Note to the `text` input of the Selector.
4.  Use the Selector's output to feed your **CLIP Text Encode**.
5.  This setup allows you to manage massive, complex prompts in an organized way while still enjoying the power of randomized variations.

-----

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

## Credits

Created by **oMo.Studio** oMo.Studio@proton.me . Optimized for high-end models like **Lumina 2**, **SDXL**, and **Flux**.



