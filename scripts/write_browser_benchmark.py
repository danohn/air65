"""Write a local browser benchmark; actual browser results are read from its DOM.

Serve the project root over loopback and open output/browser_benchmark/index.html.
The same camera path, 960x720 drawing buffer, lights, shadows and materials are
used for each case. No frame-rate improvement is inferred from polygon counts.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'output/browser_benchmark'
DEST.mkdir(parents=True,exist_ok=True)
(DEST/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Air65 browser benchmark</title><style>body{font:14px system-ui;background:#eeefeb;color:#242824;margin:24px}canvas{display:block;max-width:100%;height:auto;border:1px solid #ccc}button{padding:12px 20px}pre{white-space:pre-wrap;font:12px ui-monospace}h1{font-size:20px}#status{min-height:24px}</style><script type="importmap">{"imports":{"three":"../../site/dist/vendor/three/build/three.module.js","three/addons/":"../../site/dist/vendor/three/examples/jsm/"}}</script></head><body><h1>Air65 II — measured browser comparison</h1><p>Fixed 960 × 720 pixels, DPR 1. Same moving camera, studio and renderer. Three interleaved rounds; 60 warmup + 240 measured frames per asset per round.</p><button id="start">Start measured comparison</button><p id="status" role="status">Ready</p><div id="mount"></div><pre id="results">No results yet.</pre><script type="module" src="benchmark.js"></script></body></html>''')
(DEST/'benchmark.js').write_text(r'''
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
const cases=[['original','../refinement_baseline/web/air65-ii.glb'],['refined_full','../web/air65-ii.glb'],['refined_optimized','../web_optimized/air65-ii.glb']];
const status=document.querySelector('#status'), out=document.querySelector('#results');
const renderer=new THREE.WebGLRenderer({antialias:true, powerPreference:'high-performance', logarithmicDepthBuffer:true});
renderer.setSize(960,720); renderer.setPixelRatio(1); renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.15; renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFShadowMap;
renderer.shadowMap.autoUpdate=false;document.querySelector('#mount').append(renderer.domElement);
const scene=new THREE.Scene(); scene.background=new THREE.Color('#eeefeb');
const environment=new RoomEnvironment(), pmrem=new THREE.PMREMGenerator(renderer);
scene.environment=pmrem.fromScene(environment,.05).texture;scene.environmentIntensity=.75;environment.dispose();pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xfaf9ff,0x9b9b92,1.7));
const key=new THREE.DirectionalLight(0xfffcf4,2.5);key.position.set(-60,140,-70);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-90,right:90,top:90,bottom:-90,near:1,far:400});key.shadow.normalBias=.04;key.shadow.bias=-.0001;key.shadow.radius=3;scene.add(key);
const fill=new THREE.DirectionalLight(0xe4e9ff,1.2);fill.position.set(90,50,65);scene.add(fill);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),new THREE.ShadowMaterial({color:0x485043,opacity:.14}));floor.rotation.x=-Math.PI/2;floor.position.y=-.15;floor.receiveShadow=true;scene.add(floor);
const camera=new THREE.PerspectiveCamera(36,960/720,.2,2500);
const gl=renderer.getContext(), ext=gl.getExtension('EXT_disjoint_timer_query_webgl2'), debug=gl.getExtension('WEBGL_debug_renderer_info');
const stats=values=>{if(!values.length)return null;const v=[...values].sort((a,b)=>a-b),q=p=>v[Math.min(v.length-1,Math.floor(v.length*p))];return{n:v.length,mean_ms:values.reduce((a,b)=>a+b,0)/values.length,median_ms:q(.5),p95_ms:q(.95)};};
const models={}, runs=[], loading={}, assetIdentity={};
let invalid=false;
document.addEventListener('visibilitychange',()=>{if(document.hidden)invalid=true;});
async function run(name,round){
  const model=models[name]; scene.add(model);renderer.shadowMap.needsUpdate=true;
  camera.position.set(115,105,-138);camera.lookAt(0,22,0);await renderer.compileAsync(scene,camera);
  let frame=0,previous=0;const cpu=[],interval=[],gpu=[],pending=[];
  return await new Promise(resolve=>{
    function step(t){
      if(document.hidden){invalid=true;requestAnimationFrame(step);return;}
      const angle=(frame%300)/300*Math.PI*.9+.63;camera.position.set(Math.sin(angle)*165,98,Math.cos(angle)*-165);camera.lookAt(0,22,0);
      const measured=frame>=60;
      const query=ext&&measured?gl.createQuery():null;
      if(query)gl.beginQuery(ext.TIME_ELAPSED_EXT,query);
      const start=performance.now();renderer.render(scene,camera);const elapsed=performance.now()-start;
      if(query){gl.endQuery(ext.TIME_ELAPSED_EXT);pending.push(query);}
      if(measured){cpu.push(elapsed);if(previous)interval.push(t-previous);}
      previous=t;
      if(ext){while(pending.length&&gl.getQueryParameter(pending[0],gl.QUERY_RESULT_AVAILABLE)){const q=pending.shift();if(!gl.getParameter(ext.GPU_DISJOINT_EXT))gpu.push(gl.getQueryParameter(q,gl.QUERY_RESULT)/1e6);else invalid=true;gl.deleteQuery(q);}}
      frame++;
      if(frame%60===0)status.textContent=`Round ${round+1}/3 · ${name} · ${Math.min(frame,300)}/300 frames`;
      if(frame<300)requestAnimationFrame(step);else{
        for(const q of pending)gl.deleteQuery(q);
        const r={case:name,round:round+1,cpu_submission:stats(cpu),raf_interval:stats(interval),gpu_elapsed:stats(gpu),mean_fps:1000/stats(interval).mean_ms,renderer_info:{draw_calls:renderer.info.render.calls,triangles:renderer.info.render.triangles}};
        runs.push(r);scene.remove(model);resolve(r);
      }
    }
    requestAnimationFrame(step);
  });
}
document.querySelector('#start').onclick=async()=>{
  document.querySelector('#start').disabled=true;
  try{
    for(const [name,path] of cases){status.textContent=`Loading ${name}`;const meta=await fetch(path.replace('air65-ii.glb','model-metadata.json')).then(r=>r.json());assetIdentity[name]={sha256:meta.asset_sha256,bytes:meta.asset_bytes,triangles:meta.validation.exported_triangles};let t=performance.now();const asset=await new GLTFLoader().loadAsync(path);loading[name]=performance.now()-t;const model=asset.scene;model.scale.setScalar(1000);model.traverse(n=>{if(n.userData.default_visible===false)n.visible=false;if(n.isMesh){n.castShadow=!n.name.startsWith('prop');n.receiveShadow=true;}});models[name]=model;}
    for(let round=0;round<3;round++){for(const name of round%2?['refined_optimized','refined_full','original']:['original','refined_full','refined_optimized'])await run(name,round);}
    const report={date:new Date().toISOString(),browser:navigator.userAgent,gpu:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),three_revision:THREE.REVISION,assets:assetIdentity,buffer:[960,720],pixel_ratio:1,frame_protocol:{warmup:60,measured:240,rounds:3,interleaved:true,depth_buffer:'logarithmic',shadows:'2048 PCF, updated once per asset',motion:'identical 0.9pi camera orbit',battery_visible:false},timer_extension:!!ext,invalidated_by_background_or_gpu_disjoint:invalid,load_parse_ms:loading,runs,notes:['Frame cadence is requestAnimationFrame based and can be vsync-limited. CPU submission is not end-to-end GPU cost.','GPU elapsed is optional and excludes unavailable final pending queries. Loading includes local HTTP/parse and warm caches; it is not an internet bandwidth benchmark.','Original vs refined changes geometry/materials. Refined full vs refined optimized isolates mesh optimization using the same final authored materials.','This is one local browser/GPU/viewport, not a cross-device performance guarantee.']};
    out.textContent=JSON.stringify(report,null,2);status.textContent=invalid?'Completed with invalidation — repeat while page remains visible':'Benchmark complete';
  }catch(e){out.textContent=String(e.stack||e);status.textContent='Benchmark failed';}
};
''')
print(DEST/'index.html')
