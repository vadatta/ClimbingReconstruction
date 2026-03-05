import * as THREE from "three";
import { OneEuroVec3 } from "../filters/OneEuroFilter.js";

export function createPoseSkeleton(app){

    app.poseGroup = new THREE.Group();
    app.scene.add(app.poseGroup);

    app.pose_spheres = [];
    app.pose_filters = [];
    app.root_filters = []

    for(let i = 0; i < 33; i++){

        const geo = new THREE.SphereGeometry(0.05,16,16);
        const mat = new THREE.MeshStandardMaterial({color:'white'});
        const sphere = new THREE.Mesh(geo,mat);

        app.poseGroup.add(sphere);
        app.pose_spheres.push(sphere);

        // create vector filter
        app.pose_filters.push(
            new OneEuroVec3(1.3, 0.3, 1.0)
        );

        app.root_filter = new OneEuroVec3(0.5, 0.1,   // beta
            1.0);
    }
}