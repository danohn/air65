import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RotorMotion } from './rotor-motion.js';

const $ = (id) => document.getElementById(id);
const parts = [
  {id:'frame', label:'Air65 II frame', count:'01', color:'#afa0d4', title:'The ultralight frame', text:'82.6 × 82.6 × 15.1 mm, with a 65 mm motor diagonal and four protective ducts.', tag:'Published outer dimensions'},
  {id:'canopy', label:'Camera canopy', count:'01', color:'#dadbd2', title:'An open, sculpted canopy', text:'A lightweight arch and four mounting legs surround the camera. Its contours are reconstructed from photographs.', tag:'Reference-based shape estimate'},
  {id:'camera', label:'FPV camera', count:'01', color:'#444d47', title:'C03 V2 FPV camera', text:'Camera board, lens barrel and optical surfaces. The installed position and detailed contours include estimates.', tag:'Published component · estimated installation'},
  {id:'electronics', label:'Electronics & wiring', count:'01', color:'#b19d69', title:'The flight electronics', text:'Matrix II board with reference-based silkscreen, chip markings, packages, wiring and antenna. The body outline and small details remain photographic estimates.', tag:'Mixed published and estimated dimensions'},
  {id:'motor', label:'Brushless motors', count:'04', color:'#919598', title:'Four miniature motors', text:'0702 motors with metal bells, exposed copper windings and purple crowns. The detailed internal geometry is estimated.', tag:'Published motor type · estimated details'},
  {id:'prop', label:'Three-blade propellers', count:'04', color:'#cbd7df', title:'31 mm propellers', text:'Two clockwise and two counterclockwise propellers. Diameter is published; blade sweep and airfoil are estimated.', tag:'Published diameter · estimated blade profile'},
  {id:'battery', label:'280 mAh battery', count:'OPT', color:'#cf7549', title:'Optional 1S battery', text:'LAVA II 280 mAh, with a 54 × 10 × 6 mm nominal body, printed wrapper and black BT2.0 terminal. Display pose; the power lead is unplugged.', tag:'Published cell dimensions · display pose'},
];
const initialVisibility = Object.fromEntries(parts.map(p => [p.id, p.id !== 'battery']));
const state = { visibility:{...initialVisibility}, selected:null, explode:0, wireframe:false, view:'perspective', ready:false };
const componentNodes = [];
let scene, camera, renderer, controls, model, floor, shadowLight, resizeObserver, rotorMotion;
let raf = 0, settling = 0, previousTime = 0, contextLost = false, rendering = false;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const partCategory = id => id.startsWith('prop') ? 'prop' : id.startsWith('motor') ? 'motor' : id;

for (const part of parts) {
  const row = document.createElement('div');
  row.className = 'part-row';
  row.dataset.part = part.id;
  row.innerHTML = `<button class="part-name" data-model-control disabled aria-label="Inspect ${part.label}"><span class="part-swatch" style="background:${part.color}"></span>${part.label}<span class="part-count">${part.count}</span></button><label class="part-toggle"><input class="switch" type="checkbox" ${initialVisibility[part.id]?'checked':''} aria-label="Show ${part.label}" data-model-control disabled></label>`;
  row.querySelector('button').addEventListener('click', () => selectPart(part.id));
  row.querySelector('input').addEventListener('change', e => {
    state.visibility[part.id] = e.target.checked;
    applyVisibility();
    if (!e.target.checked && state.selected === part.id) selectPart(null);
    announce(`${part.label} ${e.target.checked?'shown':'hidden'}.`);
  });
  $('parts-list').append(row);
}

function announce(text) { $('announcement').textContent = text; }
function requestRender() {
  settling = 12;
  if (!raf && !rendering && !document.hidden && !contextLost && renderer) raf = requestAnimationFrame(render);
}
function render(time) {
  raf = 0;
  if (document.hidden || contextLost) return;
  rendering = true;
  const elapsed = previousTime ? Math.max(0, (time - previousTime) / 1000) : 0;
  const delta = Math.min(elapsed, .05);
  previousTime = time;
  rotorMotion?.update(elapsed);
  if (rotorMotion?.active && rotorMotion.effectiveRPM < 1000) renderer.shadowMap.needsUpdate = true;
  controls.update(delta);
  if (floor) floor.visible = camera.position.y > 1 && state.explode === 0 && !state.wireframe;
  renderer.render(scene, camera);
  rendering = false;
  settling--;
  if (controls.autoRotate || rotorMotion?.active || settling > 0) raf = requestAnimationFrame(render);
}

function resize() {
  if (!renderer) return;
  const {width, height} = $('canvas-mount').getBoundingClientRect();
  if (!width || !height) return;
  const previousFit = state.ready ? fittedDistance() : null;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  if (previousFit) {
    // Preserve the current orbit and relative zoom when the available aspect
    // changes, including desktop-to-phone resizing and device rotation.
    const offset = camera.position.clone().sub(controls.target);
    offset.setLength(THREE.MathUtils.clamp(offset.length() * fittedDistance() / previousFit, controls.minDistance, controls.maxDistance));
    camera.position.copy(controls.target).add(offset);
  }
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, width < 650 ? 1.4 : 1.75));
  requestRender();
}

function fittedDistance() {
  // World-space UI uses millimetres; the GLB itself retains glTF metre units.
  const vertical = THREE.MathUtils.degToRad(camera.fov);
  const horizontal = 2 * Math.atan(Math.tan(vertical / 2) * camera.aspect);
  return 60 / Math.sin(Math.min(vertical, horizontal) / 2) * (state.explode ? 1.38 : 1.05);
}

function setView(name, fit=true) {
  if (!state.ready) return;
  const directions = {
    perspective: [1, .74, -1.2], top:[0, 1, -.0001], front:[0, 0, -1], right:[1, 0, 0], bottom:[0, -1, -.0001],
  };
  state.view = name;
  controls.autoRotate = false;
  $('auto-rotate').setAttribute('aria-pressed', 'false');
  controls.target.set(0, state.explode ? 38 : 22, 0);
  const distance = fit ? fittedDistance() : camera.position.distanceTo(controls.target);
  camera.up.set(0, 1, 0);
  camera.position.copy(controls.target).add(new THREE.Vector3(...directions[name]).normalize().multiplyScalar(distance));
  // Discard residual orbit damping so presets land precisely.
  controls.enableDamping = false;
  controls.update();
  controls.enableDamping = true;
  $('view-label').textContent = `${name==='perspective'?'Perspective':name[0].toUpperCase()+name.slice(1)} view`;
  document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === name)));
  requestRender();
}

function zoom(factor) {
  if (!state.ready) return;
  const delta = camera.position.clone().sub(controls.target);
  delta.setLength(THREE.MathUtils.clamp(delta.length() * factor, controls.minDistance, controls.maxDistance));
  camera.position.copy(controls.target).add(delta);
  requestRender();
}

function applyVisibility() {
  for (const node of componentNodes) node.visible = state.visibility[node.userData.category];
  if (renderer) renderer.shadowMap.needsUpdate = true;
  requestRender();
}

function selectPart(id) {
  state.selected = id;
  for (const node of componentNodes) {
    node.traverse(object => {
      if (!object.isMesh || object.userData.blurProxy) return;
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        if (!material.emissive) continue;
        if (node.userData.category === id) {
          material.emissive.set('#7967a4'); material.emissiveIntensity = .15;
        } else {
          material.emissive.copy(material.userData.originalEmissive);
          material.emissiveIntensity = material.userData.originalEmissiveIntensity;
        }
      }
    });
  }
  document.querySelectorAll('.part-row').forEach(r => r.classList.toggle('selected', r.dataset.part === id));
  const part = parts.find(p => p.id === id);
  $('detail-kicker').textContent = part ? 'COMPONENT DETAIL' : 'REFERENCE DIMENSIONS';
  $('detail-title').textContent = part?.title ?? '65 mm wheelbase';
  $('detail-text').textContent = part?.text ?? 'Motor-to-motor diagonal. A remarkably small aircraft, built around four 31 mm propellers.';
  $('detail-tag').textContent = part?.tag ?? 'Published specification';
  if (part) {
    announce(`Selected ${part.label}. ${part.text}`);
    if (window.matchMedia('(max-width: 800px)').matches) openParts(true);
  }
  requestRender();
}

function explode(value) {
  state.explode = Number(value);
  const amount = state.explode / 100;
  // Illustrative separation only; original authored transforms are stored intact.
  const offsets = {frame:[0,0,0], canopy:[0,53,0], camera:[0,29,-13], electronics:[0,12,0], motor:[0,7,0], prop:[0,27,0], battery:[0,-18,0]};
  for (const node of componentNodes) {
    node.position.copy(node.userData.originalPosition);
    node.position.add(new THREE.Vector3(...offsets[node.userData.category]).multiplyScalar(amount / 1000));
  }
  $('explode-value').textContent = `${state.explode}%`;
  $('assembly-label').textContent = state.explode ? 'Exploded · illustrative' : 'Assembled';
  $('explode-help').textContent = state.explode ? 'Spacing is illustrative, not a measured dimension.' : 'Separate the parts to see how they fit.';
  renderer.shadowMap.needsUpdate = true;
  requestRender();
}

function toggleWireframe(enabled) {
  state.wireframe = enabled;
  if (enabled) { rotorMotion?.pause(); syncMotionControls(); }
  model?.traverse(object => {
    if (object.isMesh && !object.userData.blurProxy) for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      material.wireframe = enabled;
      if ('transmission' in material) material.transmission = enabled ? 0 : material.userData.originalTransmission;
      material.needsUpdate = true;
    }
  });
  requestRender();
}

function reset() {
  rotorMotion?.reset(); syncMotionControls(); previousTime = 0;
  state.visibility = {...initialVisibility};
  document.querySelectorAll('.part-row').forEach(row => row.querySelector('input').checked = state.visibility[row.dataset.part]);
  $('explode').value = 0;
  $('wireframe').checked = false;
  explode(0); toggleWireframe(false); selectPart(null); applyVisibility(); setView('perspective');
  announce('Model and camera reset. Motors stopped. Optional battery hidden.');
}

function syncMotionControls() {
  if (!rotorMotion) return;
  const {rpm, playing, slowMotion, effectiveRPM} = rotorMotion;
  $('motor-rpm').value = rpm;
  $('motor-rpm').setAttribute('aria-valuetext', `${rpm.toLocaleString('en-US')} RPM`);
  $('rpm-value').textContent = Math.round(rpm).toLocaleString('en-US');
  $('motor-status').textContent = rpm === 0 ? 'Stopped' : playing ? (slowMotion ? 'Slow motion' : 'Running') : 'Paused';
  $('motor-play').textContent = playing ? 'Pause' : rpm ? 'Resume' : 'Spin';
  $('motor-play').setAttribute('aria-label', playing ? 'Pause motors' : rpm ? 'Resume motors' : 'Spin motors');
  $('motor-play').setAttribute('aria-pressed', String(playing));
  $('motor-slow').checked = slowMotion;
  $('motor-help').textContent = slowMotion && playing
    ? `Time slowed 500×: displayed at ${effectiveRPM.toLocaleString('en-US', {maximumFractionDigits:1})} RPM. The slider shows the simulated speed.`
    : playing && rpm >= 1000
      ? 'High-speed blur preview. Use slow motion to see the blade movement.'
      : 'Propellers and motor bells turn together. The airframe stays fixed.';
  document.querySelectorAll('[data-rpm]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.rpm) === rpm)));
}

function changeRPM(value) {
  if (!rotorMotion) return;
  if (state.wireframe && Number(value) > 0) { $('wireframe').checked = false; toggleWireframe(false); }
  rotorMotion.setRPM(Number(value));
  previousTime = 0;
  syncMotionControls(); requestRender();
}

function openParts(open) {
  $('inspector').classList.toggle('open', open);
  document.querySelector('.workspace').classList.toggle('inspector-open', open);
  $('parts-toggle').setAttribute('aria-expanded', String(open));
}

function showFailure(message) {
  $('loading').hidden = false;
  $('loading').style.opacity = 1;
  $('loading').querySelector('.spinner').hidden = true;
  $('loading-title').textContent = 'The 3D view couldn’t open';
  $('loading-progress').textContent = message;
  $('retry').hidden = false;
  document.querySelectorAll('[data-model-control]').forEach(e => e.disabled = true);
}

async function initialize() {
  try {
    renderer = new THREE.WebGLRenderer({antialias:true, alpha:false, powerPreference:'high-performance', logarithmicDepthBuffer:true});
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = false;
    renderer.shadowMap.needsUpdate = true;
    renderer.setClearColor('#eeefeb');
    renderer.domElement.tabIndex = 0;
    renderer.domElement.setAttribute('aria-label', 'Air65 II 3D model. Drag to rotate, scroll to zoom, right-drag to pan. Keyboard: arrows rotate, plus or minus zoom, zero resets.');
    $('canvas-mount').append(renderer.domElement);
    scene = new THREE.Scene();
    scene.background = new THREE.Color('#eeefeb');
    camera = new THREE.PerspectiveCamera(36, 1, .2, 2500);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = .10;
    controls.minDistance = 24;
    controls.maxDistance = 650;
    controls.zoomSpeed = .8;
    controls.rotateSpeed = .7;
    controls.panSpeed = .7;
    controls.autoRotateSpeed = .8;
    controls.addEventListener('change', requestRender);
    controls.addEventListener('start', () => {
      if (controls.autoRotate) {controls.autoRotate = false; $('auto-rotate').setAttribute('aria-pressed','false');}
      document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed','false'));
      $('view-label').textContent = 'Free orbit';
      requestRender();
    });
    const environment = new RoomEnvironment();
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(environment, .05).texture;
    scene.environmentIntensity = .75;
    environment.dispose(); pmrem.dispose();
    scene.add(new THREE.HemisphereLight(0xfaf9ff, 0x9b9b92, 1.7));
    shadowLight = new THREE.DirectionalLight(0xfffcf4, 2.5);
    shadowLight.position.set(-60, 140, -70);
    shadowLight.castShadow = true;
    shadowLight.shadow.mapSize.set(2048,2048);
    Object.assign(shadowLight.shadow.camera, {left:-90,right:90,top:90,bottom:-90,near:1,far:400});
    shadowLight.shadow.normalBias = .04;
    shadowLight.shadow.bias = -.0001;
    shadowLight.shadow.radius = 3;
    scene.add(shadowLight);
    const fill = new THREE.DirectionalLight(0xe4e9ff, 1.2); fill.position.set(90,50,65); scene.add(fill);
    floor = new THREE.Mesh(new THREE.PlaneGeometry(1200,1200), new THREE.ShadowMaterial({color:0x485043,opacity:.14}));
    floor.rotation.x = -Math.PI/2; floor.position.y = -.15; floor.receiveShadow = true; scene.add(floor);
    resizeObserver = new ResizeObserver(resize); resizeObserver.observe($('canvas-mount')); resize();
    renderer.domElement.addEventListener('webglcontextlost', e => {e.preventDefault(); contextLost = true; showFailure('Your browser paused the graphics context. Reload the viewer to continue.');});
    const modelPromise = new GLTFLoader().loadAsync('./assets/air65-ii.glb?v=motion-1', event => {
      const percent = Math.min(100, Math.round(event.loaded / (event.total || 10441784) * 100));
      $('loading-progress').textContent = percent===100 ? 'Preparing the surfaces…' : `Loading model · ${percent}%`;
    });
    const [gltf, motionSpecification] = await Promise.all([modelPromise, fetch('./assets/motion.json').then(response => {
      if (!response.ok) throw new Error('Motion specification unavailable');
      return response.json();
    })]);
    model = gltf.scene;
    model.scale.setScalar(1000);
    model.traverse(node => {
      if (node.userData.instance_id) {
        node.userData.category = partCategory(node.userData.component_id);
        node.userData.originalPosition = node.position.clone();
        componentNodes.push(node);
        // Clone shared materials per group so selection does not tint other parts.
        node.traverse(object => {
          if (!object.isMesh) return;
          const prepare = source => {
            const mat = source.clone();
            mat.userData.originalEmissive = mat.emissive?.clone();
            mat.userData.originalEmissiveIntensity = mat.emissiveIntensity;
            mat.userData.originalTransmission = mat.transmission ?? 0;
            return mat;
          };
          object.material = Array.isArray(object.material) ? object.material.map(prepare) : prepare(object.material);
          object.castShadow = node.userData.category !== 'prop';
          object.receiveShadow = true;
          object.userData.part = node.userData.category;
        });
      }
    });
    if (componentNodes.length !== 13) throw new Error('Unexpected model component count');
    scene.add(model);
    rotorMotion = new RotorMotion(componentNodes, motionSpecification);
    $('motor-rpm').max = motionSpecification.peak_rpm;
    syncMotionControls();
    state.ready = true;
    applyVisibility(); setView('perspective');
    await renderer.compileAsync(scene,camera);
    document.querySelectorAll('[data-model-control]').forEach(e => e.disabled = false);
    renderer.render(scene,camera);
    $('loading').style.opacity = 0;
    setTimeout(() => {$('loading').hidden = true;}, 350);
    announce('Air65 II model loaded. Drag to rotate or use the camera view controls.');
    requestRender();
    let pointerStart;
    renderer.domElement.addEventListener('pointerdown', e => {pointerStart = {x:e.clientX,y:e.clientY,time:performance.now(),button:e.button};});
    renderer.domElement.addEventListener('pointerup', e => {
      if (!pointerStart || pointerStart.button !== 0 || performance.now()-pointerStart.time > 500 || Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5) return;
      const bounds = renderer.domElement.getBoundingClientRect();
      pointer.set((e.clientX-bounds.left)/bounds.width*2-1,-(e.clientY-bounds.top)/bounds.height*2+1);
      raycaster.setFromCamera(pointer,camera);
      const pickable = [];
      for (const node of componentNodes) node.traverseVisible(object => {
        if (object.isMesh && !object.userData.blurProxy) pickable.push(object);
      });
      const hit = raycaster.intersectObjects(pickable, false).find(h=>h.object.userData.part);
      selectPart(hit?.object.userData.part ?? null);
    });
    renderer.domElement.addEventListener('keydown', e => {
      if (['+','=','-','_','0','Home','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) e.preventDefault(); else return;
      if (['+','='].includes(e.key)) zoom(.86);
      else if (['-','_'].includes(e.key)) zoom(1/.86);
      else if (['0','Home'].includes(e.key)) reset();
      else {
        controls.autoRotate = false; $('auto-rotate').setAttribute('aria-pressed','false');
        const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
        if (e.key==='ArrowLeft') spherical.theta -= .12;
        if (e.key==='ArrowRight') spherical.theta += .12;
        if (e.key==='ArrowUp') spherical.phi -= .12;
        if (e.key==='ArrowDown') spherical.phi += .12;
        spherical.makeSafe(); camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));
        $('view-label').textContent = 'Free orbit';
        document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed','false'));
        requestRender();
      }
    });
  } catch (error) {
    console.error('Viewer initialization failed:', error);
    showFailure('Try reloading, or use a browser with WebGL 2 enabled. The downloadable model is still available.');
  }
}

document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
$('zoom-in').addEventListener('click', () => zoom(.82));
$('zoom-out').addEventListener('click', () => zoom(1/.82));
$('reset').addEventListener('click', reset);
$('auto-rotate').addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; $('auto-rotate').setAttribute('aria-pressed',String(controls.autoRotate)); requestRender(); });
$('show-all').addEventListener('click', () => {for(const part of parts) state.visibility[part.id]=true; document.querySelectorAll('.part-row input').forEach(i=>i.checked=true); applyVisibility(); announce('All components shown, including the optional battery.');});
$('explode').addEventListener('input', e => explode(e.target.value));
$('explode').addEventListener('change', () => {if(state.explode>40) setView(state.view);});
$('wireframe').addEventListener('change', e => toggleWireframe(e.target.checked));
$('motor-rpm').addEventListener('input', e => changeRPM(e.target.value));
document.querySelectorAll('[data-rpm]').forEach(button => button.addEventListener('click', () => changeRPM(button.dataset.rpm)));
$('motor-play').addEventListener('click', () => {
  if (!rotorMotion) return;
  if (!rotorMotion.rpm) return changeRPM(120);
  if (rotorMotion.playing) rotorMotion.pause();
  else { if (state.wireframe) { $('wireframe').checked = false; toggleWireframe(false); } rotorMotion.resume(); }
  previousTime = 0; syncMotionControls(); requestRender();
});
$('motor-slow').addEventListener('change', e => { rotorMotion?.setSlowMotion(e.target.checked); syncMotionControls(); requestRender(); });
$('parts-toggle').addEventListener('click', () => openParts(!$('inspector').classList.contains('open')));
$('parts-close').addEventListener('click', () => {openParts(false); $('parts-toggle').focus();});
$('about-open').addEventListener('click', () => $('about-dialog').showModal());
$('accuracy-open').addEventListener('click', () => $('about-dialog').showModal());
$('about-close').addEventListener('click', () => $('about-dialog').close());
$('about-dialog').addEventListener('click', e => {if(e.target===$('about-dialog')){const r=e.target.getBoundingClientRect(); if(e.clientX<r.left || e.clientX>r.right || e.clientY<r.top || e.clientY>r.bottom)e.target.close();}});
$('retry').addEventListener('click', () => location.reload());
$('fullscreen').addEventListener('click', async () => {
  try {if(document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen();} catch {announce('Full screen is unavailable in this browser.');}
});
document.addEventListener('fullscreenchange', () => {$('fullscreen').setAttribute('aria-label',document.fullscreenElement?'Exit full screen':'Enter full screen'); resize();});
if (!document.fullscreenEnabled) $('fullscreen').hidden = true;
document.addEventListener('visibilitychange', () => {if(!document.hidden){previousTime=0; requestRender();}else{cancelAnimationFrame(raf);raf=0;}});
window.addEventListener('pagehide',()=>{cancelAnimationFrame(raf);resizeObserver?.disconnect();});
window.addEventListener('pageshow', event => {
  if (event.persisted) { previousTime = 0; raf = 0; resizeObserver?.observe($('canvas-mount')); resize(); requestRender(); }
});
initialize();
