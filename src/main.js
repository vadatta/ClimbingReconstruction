import * as THREE from "three";
import { initScene } from "./scene/initScene.js";
import { addHelpers } from "./scene/helpers.js";
import { createPoseSkeleton } from "./skeleton/poseSkeleton.js";
import { createHandSkeletons } from "./skeleton/handSkeleton.js";
import { animate } from "./animation/animate.js";

const app = {};

async function main(){
    app.frame_count = 0;
    const response = await fetch("/data/climb_motion.json");

    const data = await response.json();
    app.raw_data = data;


    initScene(app);
    addHelpers(app);


    await createPoseSkeleton(app);
    await createHandSkeletons(app);


    animate(app);

}

main();