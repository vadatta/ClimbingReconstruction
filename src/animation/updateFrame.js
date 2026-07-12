import * as THREE from "three";

const LEFT_HIP = 23;
const RIGHT_HIP = 24;
const POSE_SCALE = 2.6;
const BONE_POSITION_ALPHA = 0.12;
const BONE_LENGTH_ALPHA = 0.1;
const BONE_ROTATION_ALPHA = 0.08;
const UP = new THREE.Vector3(0, 1, 0);

export function updateFrame(app){

    const frame = app.raw_data.frames[app.frame_count];
    updateGripOverlay(app, frame);

    // compute raw root
    const hipL = frame.landmarks[LEFT_HIP];
    const hipR = frame.landmarks[RIGHT_HIP];

    const root = new THREE.Vector3(
        ((hipL.x + hipR.x)/2 - 0.5)*2,
        -((hipL.y + hipR.y)/2 - 0.5)*2,
        0
    );

    frame.landmarks.forEach((lm,i)=>{

        const raw = new THREE.Vector3(
            (lm.x-0.5)*2,
            -(lm.y-0.5)*2,
            0
        );

        // compute local pose
        const local = raw.clone().sub(root).multiplyScalar(POSE_SCALE);

        // filter articulation
        const local_filtered = app.pose_filters[i].filter(local,1/30);

        app.pose_points[i].copy(local_filtered);
    });

    updatePoseBones(app);

    app.frame_count = (app.frame_count + 1) % app.raw_data.frames.length;
}

function updateGripOverlay(app, frame){
    if (!app.grip_overlay) {
        return;
    }

    app.grip_overlay.left.textContent = `Left grip: ${frame.LeftGrip ?? "Unknown"}`;
    app.grip_overlay.right.textContent = `Right grip: ${frame.RightGrip ?? "Unknown"}`;
}

export function updatePoseBones(app){
    for (const bone of app.pose_bones) {
        const start = app.pose_points[bone.start];
        const end = app.pose_points[bone.end];
        const direction = new THREE.Vector3().subVectors(end, start);
        const length = direction.length();

        if (length < 1e-6) {
            bone.mesh.visible = false;
            continue;
        }

        bone.mesh.visible = true;

        const midpoint = new THREE.Vector3().copy(start).add(end).multiplyScalar(0.5);
        const targetQuaternion = new THREE.Quaternion().setFromUnitVectors(
            UP,
            direction.normalize()
        );

        if (!bone.initialized) {
            bone.mesh.position.copy(midpoint);
            bone.mesh.quaternion.copy(targetQuaternion);
            bone.smoothedLength = length;
            bone.initialized = true;
        } else {
            bone.mesh.position.lerp(midpoint, BONE_POSITION_ALPHA);
            bone.mesh.quaternion.slerp(targetQuaternion, BONE_ROTATION_ALPHA);
            bone.smoothedLength = THREE.MathUtils.lerp(
                bone.smoothedLength,
                length,
                BONE_LENGTH_ALPHA
            );
        }

        bone.mesh.scale.set(1, bone.smoothedLength, 1);

        // Previous direct update path:
        // bone.mesh.position.copy(start).add(end).multiplyScalar(0.5);
        // bone.mesh.scale.set(1, length, 1);
        // bone.mesh.quaternion.setFromUnitVectors(UP, direction.normalize());
    }
}
