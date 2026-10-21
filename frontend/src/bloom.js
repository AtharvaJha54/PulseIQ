import * as THREE from "three";

import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";

import { renderer, scene, camera } from "./scene.js";

const composer = new EffectComposer(renderer);

composer.addPass(
    new RenderPass(scene, camera)
);

const bloom = new UnrealBloomPass(
    new THREE.Vector2(
        window.innerWidth,
        window.innerHeight
    ),
    1.8,   // strength
    0.55,  // radius
    0.05   // threshold
);

composer.addPass(bloom);

export { composer };