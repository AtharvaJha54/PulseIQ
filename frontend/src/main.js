import "./style.css";

import { scene, camera } from "./scene.js";
import { composer } from "./bloom.js";

import { stars } from "./stars.js";
import { planet } from "./planet.js";
import { ring } from "./ring.js";


// Add objects to scene
scene.add(stars);
scene.add(planet);
scene.add(ring);

// Animation Loop
function animate() {

    requestAnimationFrame(animate);

    const t = Date.now() * 0.001;

    // Planet
    planet.rotation.y += 0.002;
    planet.rotation.x = Math.sin(t * 0.6) * 0.05;

    // Ring
    ring.rotation.z += 0.001;
    ring.rotation.x =
        Math.PI / 2.5 +
        Math.sin(t * 0.4) * 0.03;

    // Stars
    stars.rotation.y += 0.00015;

    // Planet Pulse
    const pulse = 1 + Math.sin(t * 2) * 0.01;

    planet.scale.set(
        pulse,
        pulse,
        pulse
    );

    // Camera Float
    camera.position.z =
        7 + Math.sin(t * 0.4) * 0.15;

    composer.render();
}

animate();

