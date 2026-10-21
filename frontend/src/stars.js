import * as THREE from "three";

const starGeometry = new THREE.BufferGeometry();

const starVertices = [];

const starCount = 8000;

for (let i = 0; i < starCount; i++) {

    const x = (Math.random() - 0.5) * 2000;
    const y = (Math.random() - 0.5) * 2000;
    const z = (Math.random() - 0.5) * 2000;

    starVertices.push(x, y, z);

}

starGeometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(starVertices, 3)
);

const starMaterial = new THREE.PointsMaterial({

    color: 0xffffff,

    size: 1,

    transparent: true,

    opacity: 0.8,

    sizeAttenuation: true

});

const stars = new THREE.Points(
    starGeometry,
    starMaterial
);

export { stars };