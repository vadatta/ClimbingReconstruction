import * as THREE from "three";

import { updateFrame } from "./updateFrame.js";

export function animate(app){

    function loop(){

        requestAnimationFrame(loop);

        if(app.raw_data){
            updateFrame(app);
        }

        app.renderer.render(app.scene,app.camera);
    }
    loop();

}