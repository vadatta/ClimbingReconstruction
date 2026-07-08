import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export function addHelpers(app){

    const light = new THREE.DirectionalLight(0xffffff,1);
    light.position.set(5,5,5);
    app.scene.add(light);

    const ambient = new THREE.AmbientLight(0xffffff, 0.35);
    app.scene.add(ambient);

    const frameMaterial = new THREE.LineBasicMaterial({
        color: 0x4f6f9f,
        transparent: true,
        opacity: 0.45
    });
    const axisMaterial = new THREE.LineBasicMaterial({
        color: 0x8aa0c8,
        transparent: true,
        opacity: 0.35
    });

    const wallWidth = 5;
    const wallHeight = 6;
    const wallZ = -0.04;

    const frameGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-wallWidth / 2, -wallHeight / 2, wallZ),
        new THREE.Vector3(wallWidth / 2, -wallHeight / 2, wallZ),
        new THREE.Vector3(wallWidth / 2, wallHeight / 2, wallZ),
        new THREE.Vector3(-wallWidth / 2, wallHeight / 2, wallZ),
        new THREE.Vector3(-wallWidth / 2, -wallHeight / 2, wallZ)
    ]);
    app.scene.add(new THREE.Line(frameGeometry, frameMaterial));

    const verticalAxis = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, -wallHeight / 2, wallZ),
        new THREE.Vector3(0, wallHeight / 2, wallZ)
    ]);
    const horizontalAxis = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-wallWidth / 2, 0, wallZ),
        new THREE.Vector3(wallWidth / 2, 0, wallZ)
    ]);

    app.scene.add(new THREE.Line(verticalAxis, axisMaterial));
    app.scene.add(new THREE.Line(horizontalAxis, axisMaterial));

    const controls = new OrbitControls(app.camera, app.renderer.domElement);
    controls.enableDamping = true;

    app.controls = controls;
}
