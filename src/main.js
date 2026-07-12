import "./styles.css";
import { initScene } from "./scene/initScene.js";
import { addHelpers } from "./scene/helpers.js";
import { createPoseSkeleton } from "./skeleton/poseSkeleton.js";
import { animate } from "./animation/animate.js";
import { createLayout } from "./ui/layout.js";

const app = {};

async function main(){
    const layout = createLayout();
    app.viewer = layout.viewer;
    layout.onAnalyze(async (selection) => {
        layout.setStatus("Loading reconstruction preview...");

        try {
            if (!app.initialized) {
                const response = await fetch("/data/climb_motion.json");
                if (!response.ok) {
                    throw new Error(`Could not load motion data (${response.status})`);
                }

                app.raw_data = await response.json();
                app.frame_count = 0;
                layout.showAnalysis(selection);

                initScene(app);
                addHelpers(app);
                addGripOverlay(app);
                createPoseSkeleton(app);
                animate(app);
                app.initialized = true;
            } else {
                app.frame_count = 0;
                layout.showAnalysis(selection);
            }

            layout.setStatus("");
        } catch (error) {
            layout.setStatus(error.message);
        }
    });

    document.getElementById("new-attempt-button").addEventListener("click", () => {
        layout.showSetup();
    });

}

function addGripOverlay(app){
    const overlay = document.createElement("div");
    overlay.className = "grip-overlay";

    const leftGrip = document.createElement("div");
    const rightGrip = document.createElement("div");

    overlay.appendChild(leftGrip);
    overlay.appendChild(rightGrip);
    app.viewer.appendChild(overlay);

    app.grip_overlay = {
        left: leftGrip,
        right: rightGrip
    };
}

main();
