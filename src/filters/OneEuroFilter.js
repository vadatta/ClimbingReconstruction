import * as THREE from "three";


export class OneEuroFilter {
    constructor(min_cutoff, beta, d_cutoff) {
        this.min_cutoff = min_cutoff;
        this.beta = beta;
        this.d_cutoff = d_cutoff;

        this.prev = null;
        this.prev_veloc = 0;
        this.prev_filtered = null;
    }

    alpha(cutoff, dt) {
        const tau = 1 / (2 * Math.PI * cutoff);
        return 1 / (1 + tau / dt);
    }

    filter(x, dt) {
        if (this.prev === null) {
            this.prev = x;
            this.prev_filtered = x;
            return x;
        }

        // 1️⃣ Estimate velocity
        const veloc = (x - this.prev) / dt;

        // 2️⃣ Smooth velocity
        const alpha_veloc = this.alpha(this.d_cutoff, dt);
        const smoothed_veloc =
            alpha_veloc * veloc +
            (1 - alpha_veloc) * this.prev_veloc;

        // 3️⃣ Adaptive cutoff
        const cutoff =
            this.min_cutoff +
            this.beta * Math.abs(smoothed_veloc);

        // 4️⃣ Smooth position
        const pos_alpha = this.alpha(cutoff, dt);

        const x_smoothed =
            pos_alpha * x +
            (1 - pos_alpha) * this.prev_filtered;

        // 5️⃣ Update state
        this.prev = x;
        this.prev_veloc = smoothed_veloc;
        this.prev_filtered = x_smoothed;

        return x_smoothed;
    }
}

export class OneEuroVec3 {
    constructor(min_cutoff, beta, d_cutoff) {
        this.x = new OneEuroFilter(min_cutoff, beta, d_cutoff);
        this.y = new OneEuroFilter(min_cutoff, beta, d_cutoff);
        this.z = new OneEuroFilter(0.5, 0.1, d_cutoff);
    }

    filter(vec, dt) {
        return new THREE.Vector3(
        this.x.filter(vec.x, dt),
        this.y.filter(vec.y, dt),
        this.z.filter(vec.z, dt));
    }
}