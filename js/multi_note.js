import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "M_nodes.MultiNote",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "M_Multi_Note" || nodeData.name === "M_Multi_Note_One_Select") {
            const isOneSelect = nodeData.name === "M_Multi_Note_One_Select";
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            const onConfigure = nodeType.prototype.onConfigure;

            const makeExclusive = function(node, clickedWidget) {
                if (!isOneSelect) return;
                if (!clickedWidget.value) return; 
                
                for (let w of node.widgets) {
                    if (w.name.startsWith("enable_") && w !== clickedWidget) {
                        w.value = false;
                    }
                }
                app.graph.setDirtyCanvas(true, true);
            };

            const checkAndAdd = function(node) {
                let i = 1;
                let lastTextWidget = null;
                
                while (node.widgets && node.widgets.find(w => w.name === `text_${i}`)) {
                    lastTextWidget = node.widgets.find(w => w.name === `text_${i}`);
                    i++;
                }

                if (lastTextWidget && lastTextWidget.value && lastTextWidget.value.trim() !== "") {
                    addTriplet(node, i);
                    
                    const computedSize = node.computeSize();
                    node.size[1] = computedSize[1]; 
                    app.graph.setDirtyCanvas(true, true);
                }
            };

            const addTriplet = function(node, index) {
                const defaultToggleVal = isOneSelect ? false : true;
                
                node.addWidget("toggle", `enable_${index}`, defaultToggleVal, function(val) {
                    if (isOneSelect) makeExclusive(node, this);
                    checkAndAdd(node);
                });
                
                node.addWidget("text", `title_${index}`, `Title ${index}`, function() {
                    checkAndAdd(node);
                });
                
                ComfyWidgets.STRING(node, `text_${index}`, ["STRING", { multiline: true }], app);
                
                const newTextWidget = node.widgets.find(w => w.name === `text_${index}`);
                if (newTextWidget) {
                    const origCb = newTextWidget.callback;
                    newTextWidget.callback = function() {
                        if (origCb) origCb.apply(this, arguments);
                        checkAndAdd(node);
                    };
                }
            };

            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                const node = this;

                requestAnimationFrame(() => {
                    if (!node.widgets) return;
                    for (let w of node.widgets) {
                        if (w.name.startsWith("text_")) {
                            const origCb = w.callback;
                            w.callback = function() {
                                if (origCb) origCb.apply(this, arguments);
                                checkAndAdd(node);
                            };
                        } else if (w.name.startsWith("enable_")) {
                            const origCb = w.callback;
                            w.callback = function(val) {
                                if (origCb) origCb.apply(this, arguments);
                                if (isOneSelect) makeExclusive(node, this);
                                checkAndAdd(node);
                            };
                        }
                    }
                });
            };

            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) {
                    onConfigure.apply(this, arguments);
                }
                const node = this;

                if (info && info.widgets_values) {
                    const expectedSets = Math.floor(info.widgets_values.length / 3);
                    
                    for (let i = 2; i <= expectedSets; i++) {
                        if (!node.widgets.find(w => w.name === `text_${i}`)) {
                            addTriplet(node, i);
                        }
                    }

                    for (let i = 0; i < node.widgets.length; i++) {
                        if (i < info.widgets_values.length) {
                            node.widgets[i].value = info.widgets_values[i];
                        }
                    }
                    
                    const computedSize = node.computeSize();
                    node.size[1] = computedSize[1];
                }
            };
        }
    }
});