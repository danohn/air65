import * as THREE from './vendor/three/build/three.module.js';

const TAU = Math.PI * 2;
const AXIS = new THREE.Vector3(0, 1, 0);

export function advanceAngle(angle, rpm, seconds) {
  if (![angle, rpm, seconds].every(Number.isFinite) || rpm < 0 || seconds < 0) throw new Error('Invalid rotor motion input');
  return (angle + rpm / 60 * TAU * seconds) % TAU;
}

export function blurAmount(rpm, shutterSeconds = .02) {
  // A three-blade propeller repeats every 120 degrees. Show discrete blades
  // at inspection speed, then blend toward its averaged projected coverage.
  const sweptDegrees = rpm / 60 * 360 * shutterSeconds;
  const t = THREE.MathUtils.clamp((sweptDegrees - 16) / (120 - 16), 0, 1);
  return t * t * (3 - 2 * t);
}

function meshes(root) {
  const result = [];
  root.traverse(node => { if (node.isMesh) result.push(node); });
  return result;
}

function descendant(root, key, value) {
  let found;
  root.traverse(node => { if (node.userData[key] === value) found = node; });
  if (!found) throw new Error(`Missing ${key}=${value} in ${root.name}`);
  return found;
}

function makeBlurProxy(prop, bladeGroup) {
  // Derive the radial silhouette from the actual exported blade triangles.
  // This is a lightweight coverage estimate, not a Cycles exposure render.
  prop.updateWorldMatrix(true, true);
  const inverse = prop.matrixWorld.clone().invert();
  const projected = [];
  const point = new THREE.Vector3();
  let radius = 0, minY = Infinity, maxY = -Infinity;
  for (const mesh of meshes(bladeGroup)) {
    const transform = new THREE.Matrix4().multiplyMatrices(inverse, mesh.matrixWorld);
    const attribute = mesh.geometry.attributes.position;
    const vertices = [];
    for (let i = 0; i < attribute.count; i++) {
      point.fromBufferAttribute(attribute, i).applyMatrix4(transform);
      vertices.push([point.x, point.z]);
      radius = Math.max(radius, Math.hypot(point.x, point.z));
      minY = Math.min(minY, point.y); maxY = Math.max(maxY, point.y);
    }
    const index = mesh.geometry.index;
    for (let i = 0; i < (index?.count ?? attribute.count); i += 3) {
      projected.push([0, 1, 2].map(j => vertices[index ? index.getX(i + j) : i + j]));
    }
  }
  if (!(radius > 0)) throw new Error('Empty blade geometry');
  const size = 256, bins = 128;
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const context = canvas.getContext('2d', {willReadFrequently:true});
  context.fillStyle = '#fff';
  const pixel = n => (n / radius + 1) * size / 2;
  for (const triangle of projected) {
    context.beginPath();
    context.moveTo(pixel(triangle[0][0]), pixel(triangle[0][1]));
    context.lineTo(pixel(triangle[1][0]), pixel(triangle[1][1]));
    context.lineTo(pixel(triangle[2][0]), pixel(triangle[2][1]));
    context.closePath();
    context.fill();
  }
  const source = context.getImageData(0, 0, size, size).data;
  const coverage = new Float64Array(bins), counts = new Uint32Array(bins);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const r = Math.hypot(x + .5 - size / 2, y + .5 - size / 2) / (size / 2);
    const bin = Math.floor(r * bins);
    if (bin < bins) { coverage[bin] += source[(y * size + x) * 4 + 3] / 255; counts[bin]++; }
  }
  for (let i = 0; i < bins; i++) coverage[i] /= counts[i] || 1;
  const rgba = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const r = Math.hypot(x + .5 - size / 2, y + .5 - size / 2) / (size / 2);
    const bin = Math.floor(r * bins), offset = (y * size + x) * 4;
    rgba[offset] = rgba[offset + 1] = rgba[offset + 2] = 255;
    const density = bin < bins ? ((coverage[bin - 1] ?? coverage[bin]) + 2 * coverage[bin] + (coverage[bin + 1] ?? 0)) / 4 : 0;
    rgba[offset + 3] = Math.round(255 * density * .7);
  }
  const texture = new THREE.DataTexture(rgba, size, size);
  texture.magFilter = texture.minFilter = THREE.LinearFilter;
  texture.needsUpdate = true;
  const material = new THREE.MeshPhysicalMaterial({
    color:0xe1e7ed, map:texture, roughness:.28, metalness:.05,
    transparent:true, opacity:0, depthWrite:false, side:THREE.DoubleSide,
  });
  const proxy = new THREE.Mesh(new THREE.PlaneGeometry(radius * 2, radius * 2), material);
  proxy.name = `${prop.name}_exposure_preview`;
  proxy.rotation.x = -Math.PI / 2;
  proxy.position.y = (minY + maxY) / 2;
  proxy.visible = false;
  proxy.userData = {part:'prop', blurProxy:true, radius_m:radius};
  // Picking should use the real geometry, never the transparent square texture.
  proxy.raycast = () => {};
  prop.add(proxy);
  return proxy;
}

export class RotorMotion {
  constructor(components, specification, {createBlur = true} = {}) {
    this.maximumRPM = specification.peak_rpm;
    this.shutterSeconds = specification.shutter_s;
    this.rpm = 0;
    this.playing = false;
    this.angle = 0;
    this.slowMotion = false;
    this.rotors = [];
    this.props = [];
    for (const [corner, sign] of Object.entries(specification.motion.sign_by_corner)) {
      const motor = components.find(node => node.userData.instance_id === `motor_${corner}`);
      const prop = components.find(node => node.userData.instance_id === `prop_${corner}`);
      if (!motor || !prop) throw new Error(`Missing rotor pair ${corner}`);
      const rotor = descendant(motor, 'motion_role', 'rotor');
      if (rotor.userData.angular_sign !== sign) throw new Error(`Rotor direction mismatch ${corner}`);
      for (const node of [rotor, prop]) this.rotors.push({node, sign, original:node.quaternion.clone()});
      const blades = descendant(prop, 'surface_role', 'blades');
      const materials = [...new Set(meshes(blades).flatMap(mesh => Array.isArray(mesh.material) ? mesh.material : [mesh.material]))].map(material => ({
        material, opacity:material.opacity, transparent:material.transparent, depthWrite:material.depthWrite,
      }));
      this.props.push({anchor:prop, blades, materials, proxy:createBlur ? makeBlurProxy(prop, blades) : null});
    }
    this.quaternion = new THREE.Quaternion();
  }

  setRPM(value) {
    if (!Number.isFinite(Number(value))) return;
    this.rpm = THREE.MathUtils.clamp(Number(value), 0, this.maximumRPM);
    this.playing = this.rpm > 0;
    this.updateAppearance();
  }

  get effectiveRPM() { return this.playing ? this.rpm * (this.slowMotion ? .002 : 1) : 0; }
  get active() { return this.playing && this.rpm > 0; }

  update(seconds) {
    if (!this.active) return;
    this.angle = advanceAngle(this.angle, this.effectiveRPM, seconds);
    this.applyAngle();
  }

  applyAngle() {
    for (const {node, sign, original} of this.rotors) {
      this.quaternion.setFromAxisAngle(AXIS, sign * this.angle);
      node.quaternion.copy(original).multiply(this.quaternion);
    }
  }

  updateAppearance() {
    const amount = blurAmount(this.effectiveRPM, this.shutterSeconds);
    for (const {blades, materials, proxy} of this.props) {
      blades.visible = amount < .999;
      for (const {material, opacity, transparent, depthWrite} of materials) {
        const blending = amount > 0;
        if (material.transparent !== (blending || transparent)) material.needsUpdate = true;
        material.transparent = blending || transparent;
        material.depthWrite = blending ? false : depthWrite;
        material.opacity = opacity * (1 - amount);
      }
      if (proxy) { proxy.visible = amount > .001; proxy.material.opacity = amount; }
    }
  }

  pause() { this.playing = false; this.updateAppearance(); }
  resume() { this.playing = this.rpm > 0; this.updateAppearance(); }
  setSlowMotion(enabled) { this.slowMotion = enabled; this.updateAppearance(); }
  reset() {
    this.rpm = 0; this.playing = false; this.angle = 0; this.slowMotion = false;
    this.applyAngle(); this.updateAppearance();
  }
}
