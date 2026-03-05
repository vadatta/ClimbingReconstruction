import * as THREE from "three";

export function createHandSkeletons(app){

    app.leftHandGroup = new THREE.Group();
    app.rightHandGroup = new THREE.Group();

    app.scene.add(app.leftHandGroup);
    app.scene.add(app.rightHandGroup);

    app.left_hand_spheres = [];
    app.right_hand_spheres = [];

    for(let i=0;i<21;i++){

        const geo = new THREE.SphereGeometry(0.12,16,16);

        const leftMat = new THREE.MeshStandardMaterial({color:0xff4444});
        const rightMat = new THREE.MeshStandardMaterial({color:0x4444ff});

        const leftSphere = new THREE.Mesh(geo,leftMat);
        const rightSphere = new THREE.Mesh(geo,rightMat);

        app.leftHandGroup.add(leftSphere);
        app.rightHandGroup.add(rightSphere);

        app.left_hand_spheres.push(leftSphere);
        app.right_hand_spheres.push(rightSphere);

    }
}