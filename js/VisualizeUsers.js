var sceneGL, cameraGL, rendererGL;
var sceneCSS, rendererCSS, cameraCSS;
var mouse_controls;
var keyboard_controls;
var tooltip;
var clock;

var mouse = new THREE.Vector2();
var particles = new THREE.Geometry();
var temp_particles = null;
var temp_material = new THREE.PointsMaterial({color: 0xcc0000});

var raycaster = new THREE.Raycaster();

// var colors = getColors(3419, 10);
var temp_particle_system = null
var click_particle_system = null

function init(){
  // Initialize the CLOCK (time)
  clock = new THREE.Clock();

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
  mouse_controls = new THREE.TrackballControls(cameraGL);
  mouse_controls.zoomSpeed = 0.7;

  keyboard_controls = new THREE.FlyControls(cameraGL);
  keyboard_controls.movementSpeed = 1000;
  keyboard_controls.rollSpeed = Math.PI / 4.0;
  keyboard_controls.autoForward = false;
  keyboard_controls.dragToLook = false;

  // Renderers
  rendererGL = new THREE.WebGLRenderer();
  rendererGL.setClearColor(0x21a22, 1);
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
  element.style.opacity = 1;
  element.innerHTML = "Hello World! How you doing?";
  element.style.fontSize = '1.5em';
  
  // element.style.background = new THREE.Color( 0x0082fa ).getStyle();
  element.style.color = new THREE.Color(0xffffff).getStyle();

  tooltip = new THREE.CSS2DObject(element);
  
  

  

  // var tmpParticles = RandomParticles(1000, -100, 100, 10);
  var tmpParticles = CreateParticles(data);
  //var tmpParticles = CreateParticles(data);

  var near_dicks = {};
  for (var i=0, n = tmpParticles.length; i<n; i++){
    var temp_particle = tmpParticles[i];
    var temp_key = '' + parseFloat(temp_particle.geometry.x / 10).toFixed(0) + ' ' + parseFloat(temp_particle.geometry.y / 10).toFixed(0) + ' ' + parseFloat(temp_particle.geometry.z / 10).toFixed(0);

    if (temp_key in near_dicks){
      var delta_x = (2.0 * Math.random() - 1.0) * 15;
      temp_particle.geometry.x += delta_x;
      var delta_y = (2.0 * Math.random() - 1.0) * 15;
      temp_particle.geometry.y += delta_y;
      var delta_z = (2.0 * Math.random() - 1.0) * 15;
      temp_particle.geometry.z += delta_z;

    } else {
      near_dicks[temp_key] = 1;
    }
  }
  //console.log(tmpParticles);

  for (var i=0, n=tmpParticles.length; i<n; i++){
    particles.vertices.push(tmpParticles[i].geometry);
  }

  var material = new THREE.PointsMaterial({color: 0xfffffa,size:3.0});
  var particleSystem = new THREE.Points(particles, material);
  sceneGL.add(particleSystem);
  // sceneGL.fog = new THREE.FogExp2(0x99999999,0.0025);
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
      current_intersect = intersects[0].object.geometry.vertices[intersects[0].index]
      sceneGL.remove(temp_particle_system);
      var temp_material = new THREE.PointsMaterial({color: 0xcc8800,size:10.0});
      temp_particles = new THREE.Geometry();
      
      for (var i = 0; i < Math.min(current_intersect.user_data.nearest.length,10); i++) {
        close_user = intersects[0].object.geometry.vertices[current_intersect.user_data.nearest[i]]
        temp_particles.vertices.push(close_user)
        
        
        
      }


      temp_particle_system = new THREE.Points(temp_particles, temp_material);
      sceneGL.add(temp_particle_system);
    
      var tooltip_html = []
      tooltip_html.push('<div class="tooltip">')
      tooltip_html.push('<a target="_blank" href="#" class="user_image"> <span class="user_image_image" style="background-image:url(\'')
      tooltip_html.push(current_intersect.user_data.profile_image_url)
      tooltip_html.push('\')"></span> </a><div class="content"><div class="content_top"><a target="_blank" href="#" class="name">')
      tooltip_html.push(current_intersect.user_data.name)
      tooltip_html.push('</a><br><a target="_blank" href="#" class="nick">@')
      tooltip_html.push(current_intersect.user_data.screenname)
      tooltip_html.push('</a></div>')
    
      tooltip_html.push('</div>')
      tooltip.element.innerHTML = tooltip_html.join('')
      sceneCSS.add(tooltip);
    } else {
      sceneCSS.remove(tooltip);
      sceneGL.remove(temp_particle_system);
      temp_particle_system=null
    }
    
  });

  window.addEventListener("click", function(){
    //event.preventDefault();
    
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;

    var orthoPosition = new THREE.Vector3(mouse.x, mouse.y, -1);
    orthoPosition.unproject(cameraCSS);


    // Raycast
    raycaster.setFromCamera(mouse, cameraGL);
    var intersects = raycaster.intersectObjects(sceneGL.children);

    if (intersects.length > 0){
      document.getElementById('details_box').style.display='block';
      var current_intersect = intersects[0].object.geometry.vertices[intersects[0].index]
      tw_href = 'https://www.twitter.com/'+current_intersect.user_data.screenname;
      document.getElementById('user_image').href=tw_href;
      document.getElementById('user_image_image').style.backgroundImage="url('"+ current_intersect.user_data.profile_image_url +"')";
      var name_div = document.getElementById('name')
      name_div.href = tw_href;
      name_div.innerHTML = current_intersect.user_data.name;
      
      var nick_div = document.getElementById('nick')
      nick_div.href = tw_href;
      nick_div.innerHTML = current_intersect.user_data.screenname;
      document.getElementById('count').innerHTML=current_intersect.user_data.followers_count+'<span> Followers</span>'
      document.getElementById('tw_details').href='http://www.time.mk/twitter/user/'+current_intersect.user_data.screenname;
      document.getElementById('content_bottom').innerHTML=current_intersect.user_data.description
      closest = document.getElementById('closest')
      closest.innerHTML=''
      
      var click_material = new THREE.PointsMaterial({color: 0xcc0000,size:20.0});
      sceneGL.remove(click_particle_system);
      click_particle_system = new THREE.Points(temp_particles, click_material);
      sceneGL.add(click_particle_system)
      
      
      for (var i = 0; i < Math.min(current_intersect.user_data.nearest.length,10); i++) {
        close_user = intersects[0].object.geometry.vertices[current_intersect.user_data.nearest[i]]
        
        closest.innerHTML+='@'+close_user.user_data.screenname+'<br>'
      }
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

var control_method = 'mouse'

function animate(){
  var delta = clock.getDelta();

  requestAnimationFrame(animate);

  rendererGL.render(sceneGL, cameraGL);
  rendererCSS.render(sceneCSS, cameraCSS);


  if (control_method == 'mouse'){
    mouse_controls.update();
    document.getElementById('toggle').innerHTML="Mouse mode"
  }
  else{
    keyboard_controls.update(delta);
    document.getElementById('toggle').innerHTML="Keyboard mode"
  }
  // mouse_controls.update();
}

function search(){
}

function toggle_control_method(){
  if (control_method == 'keyboard'){
    control_method = 'mouse'
  }
  else{
    control_method = 'keyboard'
  }
}

function CreateParticles(data){
  var part = new Array();
  var scale = 3000.0;

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

  //console.log(minX + ' ' + maxX);
  //console.log(minY + ' ' + maxY);
  //console.log(minZ + ' ' + maxZ);

  for (var i=0; i<data.length; i++){
    var tmpPosition = new THREE.Vector3(
      scaleValue(data[i].position[0], -scale, +scale, minX, maxX), 
      scaleValue(data[i].position[1], -scale, +scale, minY, maxY),
      scaleValue(data[i].position[2], -scale, +scale, minZ, maxZ)
    );

    var tmpParticle = new Particle(tmpPosition);
    tmpParticle.geometry.user_data = data[i];
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