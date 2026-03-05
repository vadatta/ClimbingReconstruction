import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export function addHelpers(app){

    const light = new THREE.DirectionalLight(0xffffff,1);
    light.position.set(5,5,5);
    app.scene.add(light);

    const axis = new THREE.AxesHelper(10);
    app.scene.add(axis);

    const grid = new THREE.GridHelper(10,10);
    app.scene.add(grid);

    const controls = new OrbitControls(app.camera, app.renderer.domElement);
    controls.enableDamping = true;

    app.controls = controls;
}