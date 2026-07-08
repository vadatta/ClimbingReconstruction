import * as THREE from "three";
import { initScene } from "./scene/initScene.js";
import { addHelpers } from "./scene/helpers.js";
import { createPoseSkeleton } from "./skeleton/poseSkeleton.js";
import { animate } from "./animation/animate.js";

const app = {};

async function main(){
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
    overlay.style.position = "fixed";
    overlay.style.top = "16px";
    overlay.style.left = "16px";
    overlay.style.padding = "10px 12px";
    overlay.style.color = "white";
    overlay.style.background = "rgba(0, 0, 0, 0.55)";
    overlay.style.fontFamily = "monospace";
    overlay.style.fontSize = "16px";
    overlay.style.lineHeight = "1.5";
    overlay.style.border = "1px solid rgba(255, 255, 255, 0.25)";
    overlay.style.borderRadius = "6px";

    const leftGrip = document.createElement("div");
    const rightGrip = document.createElement("div");

    overlay.appendChild(leftGrip);
    overlay.appendChild(rightGrip);
    document.body.appendChild(overlay);

    app.grip_overlay = {
        left: leftGrip,
        right: rightGrip
    };
}

main();
