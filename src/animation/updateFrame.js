import * as THREE from "three";

const LEFT_HIP = 23;
const RIGHT_HIP = 24;
const LEFT_WRIST = 15;
const RIGHT_WRIST = 16;
const RIGHT_ELBOW = 14;
const LEFT_ELBOW = 13;

export function updateFrame(app){

    const frame = app.raw_data.frames[app.frame_count];

    // compute raw root
    const hipL = frame.landmarks[LEFT_HIP];
    const hipR = frame.landmarks[RIGHT_HIP];

    const root = new THREE.Vector3(
        ((hipL.x + hipR.x)/2 - 0.5)*2,
        -((hipL.y + hipR.y)/2 - 0.5)*2,
        ((hipL.z + hipR.z)/2)*2
    );

    const root_world = app.root_filter.filter(root,1/30);

    frame.landmarks.forEach((lm,i)=>{

        const raw = new THREE.Vector3(
            (lm.x-0.5)*2,
            -(lm.y-0.5)*2,
            lm.z*2
        );

        // compute local pose
        const local = raw.clone().sub(root);

        // filter articulation
        const local_filtered = app.pose_filters[i].filter(local,1/30);

        // reconstruct world position
        const world = local_filtered.add(root_world);

        app.pose_spheres[i].position.copy(world);
    });

    update_hands(app, frame);

    app.frame_count = (app.frame_count + 1) % app.raw_data.frames.length;
}

export function update_hands(app, frame){
    if (frame.LeftHand){
        const pose_wrist_world = app.pose_spheres[LEFT_WRIST];
        const pose_elbow_world = app.pose_spheres[LEFT_ELBOW];

        const pose_forearm_world = new THREE.Vector3()
        pose_forearm_world.subVectors(wrist, elbow).normalize()

        const handForward = new THREE.Vector3(0, 0, 1);

        const q = new THREE.quaternion();
        q.setFromUnitVectors(handForward, pose_forearm_world);

        const hand_wrist = new THREE.Vector3(
            (frame.LeftHand[0].x - 0.5) * 2,
            -(frame.LeftHand[0].y - 0.5) * 2,
            frame.LeftHand[0].z * 2
        );

        for (let i = 0; i < 21; i ++){
            const hand_point = new THREE.Vector3(
            (frame.LeftHand[i].x - 0.5) * 2,
            -(frame.LeftHand[i].y - 0.5) * 2,
            frame.LeftHand[i].z * 2
        );

        const local = hand_point.sub(hand_wrist);
        local.applyQuaternion(q);

        const world = local.add(pose_wrist_world);

        app.leftHandSpheres[i].position.copy(world);

    }
    if (frame.RightHand){
        const pose_wrist_world = app.pose_spheres[RIGHT_WRIST];
        const pose_elbow_world = app.pose_spheres[RIGHT_ELBOW];

        const forearm = new THREE.Vector3()
        forearm.subVectors(pose_wrist_world, pose_elbow_world).normalize()

        const handForward = new THREE.Vector3(0, 0, 1);

        const q = new THREE.quaternion();
        q.setFromUnitVectors(handForward, forearm);

        const hand_wrist = new THREE.Vector3(
            (frame.RightHand[0].x - 0.5) * 2,
            -(frame.RightHand[0].y - 0.5) * 2,
            frame.RightHand[0].z * 2
        );

        for (let i = 0; i < 21; i ++){
            const hand_point = new THREE.Vector3(
            (frame.RightHand[i].x - 0.5) * 2,
            -(frame.RightHand[i].y - 0.5) * 2,
            frame.RightHand[i].z * 2
        );

        const local = hand_point.sub(hand_wrist);
        local.apply(q);
        const world = local.add(pose_wrist_world);

        app.leftHandSpheres[i].position.copy(world);

    }
}