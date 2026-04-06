import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MoMo.SaveJPGAdvanced",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Check if we are modifying the correct node based on its Python ID
        if (nodeData.name === "M_Save_JPG_Advanced") {
            
            // Store the original function for node creation
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            // Override it with our custom logic
            nodeType.prototype.onNodeCreated = function () {
                // Call the original function to render the node normally
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // --- CUSTOM LOGIC ---
                // Default number for a new group (group 1 is created by Python by default)
                this.m_group_count = 2; 

                // Function to check how many trios exist after loading a workflow
                // (prevents the counter from resetting to 2 after a refresh and overwriting existing data)
                const updateCountFromExisting = () => {
                    let maxCount = 1;
                    if (this.inputs) {
                        for (let i = 0; i < this.inputs.length; i++) {
                            // Look for wires named positive_2, positive_3, etc.
                            const match = this.inputs[i].name.match(/positive_(\d+)/);
                            if (match) {
                                maxCount = Math.max(maxCount, parseInt(match[1], 10));
                            }
                        }
                    }
                    this.m_group_count = maxCount + 1;
                };

                updateCountFromExisting();

                // Add a clickable button directly to the node to add inputs
                this.addWidget("button", "+ Add Target Trio", "button", () => {
                    const i = this.m_group_count;
                    
                    // Safety limit (matches the Python loop limit of 20)
                    if (i > 20) {
                        alert("Maximum limit of 20 groups reached.");
                        return;
                    }

                    // 1. Add a text field for naming the group (Widget)
                    this.addWidget("text", `group_name_${i}`, `Group ${i}`);

                    // 2. Add three connection slots for wires (Inputs)
                    this.addInput(`positive_${i}`, "STRING");
                    this.addInput(`negative_${i}`, "STRING");
                    this.addInput(`seed_${i}`, "INT");

                    // Increment the counter for the next click
                    this.m_group_count++;
                    
                    // Automatically resize the node to fit the new elements
                    const sz = this.computeSize();
                    this.size[0] = Math.max(this.size[0], sz[0]);
                    this.size[1] = Math.max(this.size[1], sz[1]);
                    
                    // Redraw the graph to show changes
                    app.graph.setDirtyCanvas(true, true);
                });

                // Add a clickable button to remove the last added trio
                this.addWidget("button", "- Remove Target Trio", "button", () => {
                    // Prevent removing the base group (group 1 is fixed and hardcoded in Python)
                    if (this.m_group_count <= 2) {
                        return; 
                    }

                    const targetIdx = this.m_group_count - 1;

                    // Find and remove the group name widget
                    const widgetIdx = this.widgets.findIndex(w => w.name === `group_name_${targetIdx}`);
                    if (widgetIdx !== -1) {
                        this.widgets.splice(widgetIdx, 1);
                    }

                    // Find and remove the inputs backwards to avoid array index shifting issues
                    for (let j = this.inputs.length - 1; j >= 0; j--) {
                        const inp = this.inputs[j];
                        if (inp.name === `positive_${targetIdx}` || 
                            inp.name === `negative_${targetIdx}` || 
                            inp.name === `seed_${targetIdx}`) {
                            this.removeInput(j);
                        }
                    }

                    // Decrement the counter
                    this.m_group_count--;
                    
                    // Recalculate size downwards so the node shrinks when inputs are removed
                    const sz = this.computeSize();
                    this.size[0] = Math.max(this.size[0], sz[0]);
                    this.size[1] = sz[1]; // Do not use Math.max here, otherwise it won't shrink
                    
                    // Redraw the graph to show changes
                    app.graph.setDirtyCanvas(true, true);
                });

                return r;
            };
        }
    }
});