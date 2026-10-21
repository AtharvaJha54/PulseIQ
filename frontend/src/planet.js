import * as THREE from "three";

const planet = new THREE.Group();

const geometry = new THREE.SphereGeometry(1, 128, 128);

const material = new THREE.ShaderMaterial({

    transparent: true,

    depthWrite: false,

    side: THREE.DoubleSide,

    blending: THREE.NormalBlending,

    uniforms: {

        glowColor: {
            value: new THREE.Color(0x58c8ff)
        }

    },

    vertexShader: `

        varying vec3 vNormal;
        varying vec3 vView;

        void main(){

            vec4 worldPosition =
                modelMatrix * vec4(position,1.0);

            vNormal =
                normalize(normalMatrix * normal);

            vView =
                normalize(cameraPosition - worldPosition.xyz);

            gl_Position =
                projectionMatrix *
                viewMatrix *
                worldPosition;

        }

    `,

    fragmentShader: `

uniform vec3 glowColor;

varying vec3 vNormal;
varying vec3 vView;

void main(){

    float fresnel = pow(
        abs(dot(normalize(vNormal), normalize(vView))),
        2.8
    );

    fresnel = 1.0 - fresnel;

    vec3 color = glowColor * fresnel;

    gl_FragColor = vec4(
        color,
        fresnel * 0.75
    );

}
`

});

const sphere = new THREE.Mesh(
    geometry,
    material
);

planet.add(sphere);

export { planet };