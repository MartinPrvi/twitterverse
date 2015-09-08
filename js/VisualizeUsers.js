var sceneGL, cameraGL, rendererGL;
var sceneCSS, rendererCSS, cameraCSS;
var controls;
var tooltip;

var mouse = new THREE.Vector2();
var particles = new THREE.Geometry();

var raycaster = new THREE.Raycaster();

// var colors = getColors(3419, 10);

function init(){
  // height and width of window
  var height = window.innerHeight;
  var width = window.innerWidth;

  // GL and CSS scene
  sceneGL = new THREE.Scene();
  sceneCSS = new THREE.Scene();

  // Camera
  cameraGL = new THREE.PerspectiveCamera(45, width / height, 1, 10000);
  cameraGL.position.set(0, 300, 300);

  var viewSize = 900;
  var aspectRation = width / height;
  cameraCSS = new THREE.OrthographicCamera( width / - 2, width / 2, height / 2, height / - 2, 1, 1000 );
  cameraCSS.position.set(0, 0, 10);

  // Controls
  controls = new THREE.TrackballControls(cameraGL);
  controls.zoomSpeed = 0.7;

  // Renderers
  rendererGL = new THREE.WebGLRenderer();
  rendererGL.setClearColor(0x333F47, 1);
  rendererGL.setSize(width, height);
  rendererGL.sortObjects = false;
  document.body.appendChild(rendererGL.domElement);

  rendererCSS = new THREE.CSS2DRenderer();
  rendererCSS.setSize(width, height);
  rendererCSS.domElement.style.position = 'absolute';
  rendererCSS.domElement.style.top = 0;
  document.body.appendChild(rendererCSS.domElement);

  // Objects
  var element = document.createElement( 'div' );
  // element.style.width = '100px';
  // element.style.height = '100px';
  element.style.opacity = 0.5;
  element.innerHTML = "Hello World! How you doing?";
  element.style.fontSize = '1.5em';
  // element.style.background = new THREE.Color( 0x0082fa ).getStyle();
  element.style.color = new THREE.Color(0xffffff).getStyle();

  tooltip = new THREE.CSS2DObject(element);

  // var tmpParticles = RandomParticles(1000, -100, 100, 10);
  var tmpParticles = CreateParticles(data);

  console.log(tmpParticles);

  for (var i=0, n=tmpParticles.length; i<n; i++){
    particles.vertices.push(tmpParticles[i].geometry);
  }

  var particleSystem = new THREE.ParticleSystem(particles);
  sceneGL.add(particleSystem);

  window.addEventListener("mousemove", function(){
    event.preventDefault();

    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;

    var orthoPosition = new THREE.Vector3(mouse.x, mouse.y, -1);
    orthoPosition.unproject(cameraCSS);

    tooltip.position.x = orthoPosition.x;
    tooltip.position.y = orthoPosition.y + 30;

    // Raycast
    raycaster.setFromCamera(mouse, cameraGL);
    var intersects = raycaster.intersectObjects(sceneGL.children);

    if (intersects.length > 0){
      console.log(intersects[0]);
      tooltip.element.innerHTML = "Screen Name: " + intersects[0].object.geometry.vertices[intersects[0].index].screenname;
      sceneCSS.add(tooltip);
    } else {
      sceneCSS.remove(tooltip);
    }
    
  });

  window.addEventListener("resize", function(){
    var WIDTH = window.innerWidth;
    var HEIGHT = window.innerHeight;

    rendererGL.setSize(WIDTH, HEIGHT);
    rendererCSS.setSize(WIDTH, HEIGHT);

    cameraGL.aspect = WIDTH / HEIGHT;
    cameraGL.updateProjectionMatrix();

    cameraCSS.left = - width / 2;
    cameraCSS.right = width / 2;
    cameraCSS.top = height / 2;
    cameraCSS.bottom = - height / 2;
    cameraCSS.updateProjectionMatrix();
  });

}

function animate(){
  requestAnimationFrame(animate);

  rendererGL.render(sceneGL, cameraGL);
  rendererCSS.render(sceneCSS, cameraCSS);

  controls.update();
}

function CreateParticles(data){
  var part = new Array();
  var scale = 1000.0;

  var minX = +Infinity;
  var maxX = -Infinity;
  var minY = +Infinity;
  var maxY = -Infinity;
  var minZ = +Infinity;
  var maxZ = -Infinity;

  for (var i=0; i<data.length; i++){

    if (data[i].position[0] < minX) minX = data[i].position[0];
    if (data[i].position[0] > maxX) maxX = data[i].position[0];
    if (data[i].position[1] < minY) minY = data[i].position[1];
    if (data[i].position[1] > maxY) maxY = data[i].position[1];
    if (data[i].position[2] < minZ) minZ = data[i].position[2];
    if (data[i].position[2] > maxZ) maxZ = data[i].position[2];
  }

  console.log(minX + ' ' + maxX);
  console.log(minY + ' ' + maxY);
  console.log(minZ + ' ' + maxZ);

  for (var i=0; i<data.length; i++){
    var tmpPosition = new THREE.Vector3(
      scaleValue(data[i].position[0], -scale, +scale, minX, maxX), 
      scaleValue(data[i].position[1], -scale, +scale, minY, maxY),
      scaleValue(data[i].position[2], -scale, +scale, minZ, maxZ)
    );

    var tmpParticle = new Particle(tmpPosition);
    tmpParticle.geometry.screenname = data[i].screenname;
    part.push(tmpParticle);         
  }

  return part;
}

function Particle(positionV3){

  this.geometry = new THREE.Vector3(0, 0, 0);
  this.positionV3 = positionV3;
  
  // this.material = new THREE.MeshLambertMaterial({color: 0x55b663});
  // this.mesh = new THREE.Mesh(this.geometry, this.material);

  this.geometry.x = this.positionV3.x;
  this.geometry.y = this.positionV3.y;
  this.geometry.z = this.positionV3.z;
}

function scaleValue(value, a, b, min, max){
  var result = ((value - min) * (b - a) / (max - min)) + a;

  return result;
}

function hex2rgb(h) {
  return [(h & (255 << 16)) >> 16, (h & (255 << 8)) >> 8, h & 255];
}

function distance(a, b) {
  var d = [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  return Math.sqrt((d[0]*d[0]) + (d[1]*d[1]) + (d[2]*d[2]));
}

function freshColor(sofar, d) {
  var n, ok;
  while(true) {
      ok = true;
      n = Math.random()*0xFFFFFF<<0;
      for(var c in sofar) {
          if(distance(hex2rgb(sofar[c]), hex2rgb(n)) < d) {
              ok = false;
              break;
          }
      }
      if(ok) { return n; }
  }
}

function getColors(n, d) {
  var a = [];
  for(; n > 0; n--) {
      a.push(freshColor(a, d));
  }
  return a;
}