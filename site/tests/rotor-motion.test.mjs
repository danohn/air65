import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from '../dist/vendor/three/build/three.module.js';
import {RotorMotion, advanceAngle, blurAmount} from '../dist/rotor-motion.js';

const specification = JSON.parse(readFileSync(new URL('../dist/assets/motion.json', import.meta.url)));

// Load the actual shipped node hierarchy without a browser, textures or WebGL.
function modelHierarchy() {
  const glb = readFileSync(new URL('../dist/assets/air65-ii.glb', import.meta.url));
  const document = JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString());
  const nodes = document.nodes.map(definition => {
    const node = new THREE.Group();
    node.name = definition.name;
    node.userData = structuredClone(definition.extras ?? {});
    if (definition.matrix) new THREE.Matrix4().fromArray(definition.matrix).decompose(node.position, node.quaternion, node.scale);
    else {
      if (definition.translation) node.position.fromArray(definition.translation);
      if (definition.rotation) node.quaternion.fromArray(definition.rotation);
      if (definition.scale) node.scale.fromArray(definition.scale);
    }
    if (definition.mesh !== undefined) for (const primitive of document.meshes[definition.mesh].primitives) {
      const accessor = document.accessors[primitive.attributes.POSITION];
      // A point off the pivot lets tests detect unintended geometry motion.
      const geometry = new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(accessor.max, 3));
      node.add(new THREE.Mesh(geometry, new THREE.MeshBasicMaterial()));
    }
    return node;
  });
  document.nodes.forEach((definition, index) => { for (const child of definition.children ?? []) nodes[index].add(nodes[child]); });
  const scene = new THREE.Scene();
  for (const root of document.scenes[document.scene ?? 0].nodes) scene.add(nodes[root]);
  scene.updateMatrixWorld(true);
  return {scene, components:nodes.filter(node => node.userData.instance_id)};
}

test('RPM integrates independently of rendering frame rate', () => {
  let coarse = 0, fine = 0;
  for (let i = 0; i < 100; i++) coarse = advanceAngle(coarse, 17123, .1);
  for (let i = 0; i < 250; i++) fine = advanceAngle(fine, 17123, .04);
  assert.ok(Math.abs(coarse - fine) < 1e-9);
  assert.ok(Math.abs(advanceAngle(0, 120, .125) - Math.PI / 2) < 1e-12);
});

test('blur preserves inspection speeds and covers repeated blades at high RPM', () => {
  assert.equal(blurAmount(0), 0);
  assert.equal(blurAmount(120), 0);
  assert.ok(blurAmount(500) > 0 && blurAmount(500) < 1);
  assert.equal(blurAmount(1000), 1);
  assert.equal(blurAmount(specification.peak_rpm), 1);
});

test('actual shipped hierarchy rotates eight rotor anchors, preserving stators and body', () => {
  const {scene, components} = modelHierarchy();
  const motion = new RotorMotion(components, specification, {createBlur:false});
  assert.equal(components.length, 13);
  assert.equal(motion.rotors.length, 8);
  const stationary = [];
  scene.traverse(node => {
    let moving = false;
    for (let ancestor = node; ancestor; ancestor = ancestor.parent) {
      if (ancestor.userData.motion_role === 'rotor' || ancestor.userData.instance_id?.startsWith('prop_')) moving = true;
    }
    if (node.isMesh && !moving) stationary.push({node, before:node.matrixWorld.clone()});
  });
  motion.setRPM(120); motion.update(.125); scene.updateMatrixWorld(true);
  for (const {node, before} of stationary) assert.deepEqual(node.matrixWorld.elements, before.elements, node.name);
  assert.ok(stationary.length > 40);
  for (const {node, original, sign} of motion.rotors) {
    const relative = original.clone().invert().multiply(node.quaternion);
    assert.ok(Math.abs(relative.y - sign * Math.SQRT1_2) < 1e-12, node.name);
  }
});

test('pause, slow motion, reset and exploded offsets remain independent', () => {
  const {scene, components} = modelHierarchy();
  const motion = new RotorMotion(components, specification, {createBlur:false});
  motion.setRPM(999999); assert.equal(motion.rpm, 60394);
  motion.setSlowMotion(true); assert.equal(motion.effectiveRPM, 120.788);
  const prop = components.find(node => node.userData.instance_id === 'prop_FL');
  prop.position.y += .03;
  const exploded = prop.position.clone();
  motion.update(.125); scene.updateMatrixWorld(true);
  assert.ok(prop.position.equals(exploded));
  motion.pause(); const pausedAngle = motion.angle; motion.update(2);
  assert.equal(motion.angle, pausedAngle);
  assert.equal(motion.effectiveRPM, 0);
  assert.ok(motion.props.every(prop => prop.blades.visible));
  motion.resume(); assert.equal(motion.effectiveRPM, 120.788);
  motion.reset(); assert.equal(motion.rpm, 0); assert.equal(motion.angle, 0);
  assert.equal(motion.playing, false); assert.equal(motion.slowMotion, false);
  assert.ok(prop.position.equals(exploded));
  for (const {node, original} of motion.rotors) assert.ok(node.quaternion.equals(original));
});
