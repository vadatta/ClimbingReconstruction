import * as THREE from "three";
import { OneEuroVec3 } from "../filters/OneEuroFilter.js";

export const POSE_BONES = [
    [11, 12], // shoulders
    [11, 13], [13, 15], // left arm
    [12, 14], [14, 16], // right arm
    [11, 23], [12, 24], // torso
    [23, 24], // hips
    [23, 25], [25, 27], // left leg
    [24, 26], [26, 28], // right leg
    [27, 29], [29, 31], // left foot
    [28, 30], [30, 32], // right foot
];

export function createPoseSkeleton(app){

    app.poseGroup = new THREE.Group();
    app.scene.add(app.poseGroup);

    app.pose_points = [];
    app.pose_filters = [];
    app.pose_bones = [];

    for(let i = 0; i < 33; i++){
        app.pose_points.push(new THREE.Vector3());

        // create vector filter
        app.pose_filters.push(
            new OneEuroVec3(0.25, 0.005, 0.6)
        );

        // Old landmark sphere debug view:
        // const geo = new THREE.SphereGeometry(0.05,16,16);
        // const mat = new THREE.MeshStandardMaterial({color:'white'});
        // const sphere = new THREE.Mesh(geo,mat);
        // app.poseGroup.add(sphere);
        // app.pose_spheres.push(sphere);
    }

    const boneGeometry = new THREE.CylinderGeometry(0.025, 0.025, 1, 12);
    const boneMaterial = new THREE.MeshStandardMaterial({color: 'white'});

    for (const [start, end] of POSE_BONES) {
        const bone = new THREE.Mesh(boneGeometry, boneMaterial);

        app.poseGroup.add(bone);
        app.pose_bones.push({
            start,
            end,
            mesh: bone,
            initialized: false,
            smoothedLength: 1
        });
    }
}
