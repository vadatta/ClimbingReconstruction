import * as THREE from "three";

export function initScene(app){
    const viewer = app.viewer || document.body;
    const { width, height } = viewer.getBoundingClientRect();

    app.scene = new THREE.Scene();
    app.scene.background = new THREE.Color("black");

    app.camera = new THREE.PerspectiveCamera(
        75,
        width / height,
        0.1,
        1000
    );

    app.camera.position.z = 5;

    app.renderer = new THREE.WebGLRenderer({ antialias:true });

    app.renderer.setSize(width, height);

    viewer.appendChild(app.renderer.domElement);

    window.addEventListener("resize", () => {
        const { width: nextWidth, height: nextHeight } = viewer.getBoundingClientRect();

        app.camera.aspect = nextWidth / nextHeight;
        app.camera.updateProjectionMatrix();
        app.renderer.setSize(nextWidth, nextHeight);
    });

}
