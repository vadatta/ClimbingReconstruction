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
    app.frame_count = 0;
    const response = await fetch("/data/climb_motion.json");

    const data = await response.json();
    app.raw_data = data;


    initScene(app);
    addHelpers(app);
    addGripOverlay(app);


    await createPoseSkeleton(app);
    // Hand landmark spheres are disabled while the main view uses body limb cylinders.
    // await createHandSkeletons(app);


    animate(app);

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
