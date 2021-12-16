let scene = new THREE.Scene();
const C_WIDTH = 400;
const C_HEIGHT = 300;
const aspect = C_WIDTH / C_HEIGHT;

const LEG_LENGTH = 20;
const LONG_LEG_DISTANCE = 40, LAT_LEG_DISTANCE = 10;
const axesHelper = new THREE.AxesHelper( 50 );

let FL_leg = new leg("FL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2);
let RL_leg = new leg("RL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2);
let FR_leg = new leg("FR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2);
let RR_leg = new leg("RR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2);

// Camera
let camera = new THREE.PerspectiveCamera( 60, aspect, 0.1, 1000 );
camera.position.x = 0;
camera.position.y = -100;
camera.position.z = -20;
camera.up = new THREE.Vector3(0,0,1);
camera.lookAt(new THREE.Vector3(0,0,0));
//camera.rotation.z = 20 * Math.PI / 180
camera.updateProjectionMatrix();
// var controls = new THREE.OrbitControls( camera );

// Renderer
let renderer = new THREE.WebGLRenderer( { canvas: myCanvas3d } );
renderer.setSize(C_WIDTH, C_HEIGHT);
document.body.appendChild( renderer.domElement );

scene.add( axesHelper );

let material = new THREE.MeshBasicMaterial( {color: 0x0000FF} );
let geometry = new THREE.BoxGeometry( LONG_LEG_DISTANCE, LAT_LEG_DISTANCE, 3 );
let base = new THREE.Mesh( geometry, material );
scene.add( base );

let shoulderFL = new THREE.Object3D();
let shoulderFR = new THREE.Object3D();
let shoulderRL = new THREE.Object3D();
let shoulderRR = new THREE.Object3D();
let kneeFL = new THREE.Object3D();
let kneeFR = new THREE.Object3D();
let kneeRL = new THREE.Object3D();
let kneeRR = new THREE.Object3D();

drawLeg(shoulderFL, kneeFL, FL_leg);
drawLeg(shoulderFR, kneeFR, FR_leg);
drawLeg(shoulderRL, kneeRL, RL_leg);
drawLeg(shoulderRR, kneeRR, RR_leg);

function drawLeg(shoulder, knee, leg){

  shoulder = new THREE.Object3D();
  shoulder.translateX(leg.longPos);
  shoulder.translateY(leg.latPos);
  base.add(shoulder);

  geometry = new THREE.SphereGeometry( 2, 32, 16 );
  material = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
  let sphereShoulder = new THREE.Mesh( geometry, material );
  shoulder.add( sphereShoulder );

  material = new THREE.MeshBasicMaterial( {color: 0xff0000} );
  geometry = new THREE.BoxGeometry(2, 2, LEG_LENGTH);
  let higherArm = new THREE.Mesh( geometry, material );
  higherArm.translateZ(-LEG_LENGTH/2);
  shoulder.add(higherArm);

  knee = new THREE.Object3D();
  knee.translateZ(-LEG_LENGTH/2);
  higherArm.add(knee);

  geometry = new THREE.SphereGeometry( 2, 32, 16 );
  material = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
  let sphereKnee = new THREE.Mesh( geometry, material );
  knee.add( sphereKnee );

  material = new THREE.MeshBasicMaterial( {color: 0x00ff00} );
  geometry = new THREE.BoxGeometry(2, 2, LEG_LENGTH);
  let lowerArm = new THREE.Mesh( geometry, material );
  lowerArm.translateZ(-LEG_LENGTH/2);
  knee.add(lowerArm);

  geometry = new THREE.SphereGeometry( 2, 32, 16 );
  material = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
  let sphereFoot = new THREE.Mesh( geometry, material );
  sphereFoot.translateZ(-LEG_LENGTH);
  knee.add( sphereFoot );

  if(leg.name=="FL"){
    shoulderFL = shoulder;
    kneeFL = knee;
  }
  else if(leg.name=="FR"){
    shoulderFR = shoulder;
    kneeFR = knee;
  }
  else if(leg.name=="RL"){
    shoulderRL = shoulder;
    kneeRL = knee;
  }
  else if(leg.name=="RR"){
    shoulderRR = shoulder;
    kneeRR = knee;
  }
}


// Light
let light = new THREE.DirectionalLight(0xffffff, 1.0);
light.position.set(100, 50, 100);
light.target = base;
scene.add(light);

light = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(light);


// Options (DAT.GUI)
let options = {
  base: 0,
  shoulderFL: -60,
  shoulderFR: -60,
  shoulderRL: -60,
  shoulderRR: -60,
  kneeFL: 120,
  kneeFR: 120,
  kneeRL: 120,
  kneeRR: 120,
  hipFL: 0,
  hipFR: 0,
  hipRL: 0,
  hipRR: 0,
};
// DAT.GUI Related Stuff
let gui = new dat.GUI();
gui.add(options, 'base', -180, 180).listen();
gui.add(options, 'shoulderFL', -90, 90).listen();
gui.add(options, 'shoulderFR', -90, 90).listen();
gui.add(options, 'shoulderRL', -90, 90).listen();
gui.add(options, 'shoulderRR', -90, 90).listen();
gui.add(options, 'kneeFL', 0, 180).listen();
gui.add(options, 'kneeFR', 0, 180).listen();
gui.add(options, 'kneeRL', 0, 180).listen();
gui.add(options, 'kneeRR', 0, 180).listen();
gui.add(options, 'hipFL', -90, 90).listen();
gui.add(options, 'hipFR', -90, 90).listen();
gui.add(options, 'hipRL', -90, 90).listen();
gui.add(options, 'hipRR', -90, 90).listen();

// Rendering
let xAxis = new THREE.Vector3(1, 0, 0);
let yAxis = new THREE.Vector3(0, 1, 0);
let zAxis = new THREE.Vector3(0, 0, 1);

let render = function () {
  requestAnimationFrame( render );
  
  // Rotate joints
  base.setRotationFromAxisAngle(zAxis, options.base * Math.PI / 180)

  shoulderFL.setRotationFromAxisAngle(yAxis, -FL_leg.theta1);
  shoulderFR.setRotationFromAxisAngle(yAxis, -FR_leg.theta1);
  shoulderRL.setRotationFromAxisAngle(yAxis, -RL_leg.theta1);
  shoulderRR.setRotationFromAxisAngle(yAxis, -RR_leg.theta1);
  
  kneeFL.setRotationFromAxisAngle(yAxis, -FL_leg.theta2);
  kneeFR.setRotationFromAxisAngle(yAxis, -FR_leg.theta2);
  kneeRL.setRotationFromAxisAngle(yAxis, -RL_leg.theta2);
  kneeRR.setRotationFromAxisAngle(yAxis, -RR_leg.theta2);

  // Render
  renderer.render( scene, camera );
};

render();
