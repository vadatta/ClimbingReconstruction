import * as THREE from "three";

export function initScene(app){

    app.scene = new THREE.Scene();
    app.scene.background = new THREE.Color("black");

    app.camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );

    app.camera.position.z = 5;

    app.renderer = new THREE.WebGLRenderer({ antialias:true });

    app.renderer.setSize(window.innerWidth, window.innerHeight);

    document.body.appendChild(app.renderer.domElement);

}