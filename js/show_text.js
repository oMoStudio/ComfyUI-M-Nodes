import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "M_nodes.ShowText",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "M_ShowText") {
            
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) onExecuted.apply(this, arguments);
                
                // Check if a message with text arrives from Python (e.g., in Always Update mode
                if (this.widgets && message.text_display) {
                    const widget = this.widgets.find((w) => w.name === "text_display");
                    if (widget) {
                        // Update the text box value with the incoming text
                        widget.value = message.text_display[0];
                        
                       // Dynamically resize the node height based on the text length
                        this.size[1] = Math.max(this.computeSize()[1], this.size[1]);
                        app.graph.setDirtyCanvas(true, false);
                    }
                }
            };
        }
    }
});