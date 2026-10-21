import * as THREE from "three";

const ringGeometry = new THREE.TorusGeometry(
    1.9,
    0.01,
    32,
    400
);

const ringMaterial = new THREE.MeshBasicMaterial({

    color: 0x7fd8ff,

    transparent: true,

    opacity: 0.95

});

const ring = new THREE.Mesh(
    ringGeometry,
    ringMaterial
);

ring.rotation.x = Math.PI / 2.5;
ring.rotation.z = 0.35;

export { ring };