const SX = 10;
const SY = 25;
const EX = 0;
const EY = 25;
const REFRESH = 100;


/* Medium point coordinates: (X1, Y1)
   End point coordinates:    (X2, Y2)
   Top leg length:           L1
   Bottom leg length:        L2 
   Top leg angle:            theta1
   Bottom leg angle:         theta2 */
function leg(L1, L2, theta1, theta2, longPos, latPos){
   this.L1 = L1;
   this.L2 = L2;
   this.theta1 = theta1;
   this.theta2 = theta2;
   this.longPos = longPos;
   this.latPos = latPos;
   this.direction = 1;

   // recalculate bezier curve
   this.sx = SX;
   this.sy = SY;
   this.c1x = this.sx;
   this.c1y = this.sy+5*this.direction;
   this.ex = EX;
   this.ey = EY;
   this.c2x = this.ex;
   this.c2y = this.ey+5*this.direction;
}

// Move leg
leg.prototype.setTheta1 = function(angle){
   this.theta1 = angle;
};

leg.prototype.setTheta2 = function(angle){
   this.theta2 = angle;
};

leg.prototype.setTarget = function(x, y){
   this.X2 = x;
   this.Y2 = y;
}

leg.prototype.setPath = function(t){
   let vals = this.getBezierXY(t);
   this.X2 = vals.x;
   this.Y2 = vals.y;
}

leg.prototype.reversePath = function(t){
   this.direction = -this.direction;
   // recalculate bezier curve
   this.sx = SX;
   this.sy = SY;
   this.c1x = this.sx;
   this.c1y = this.sy+5*this.direction;
   this.ex = EX;
   this.ey = EY;
   this.c2x = this.ex;
   this.c2y = this.ey+5*this.direction;
}

// Forward kinematics
leg.prototype.getX1 = function(){
   this.X1 = this.L1*Math.sin(this.theta1);
   return this.X1;
};

leg.prototype.getY1 = function(){
   this.Y1 = this.L1*Math.cos(this.theta1);
   return this.Y1;
};

leg.prototype.getZ1 = function(){
   this.Z1 = 0;
   return this.Z1;
};

leg.prototype.getX2 = function(){
   this.X2 = this.L2*Math.cos(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.sin(this.theta1);
   return this.X2;
};

leg.prototype.getY2 = function(){
   this.Y2 = this.L2*Math.sin(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.cos(this.theta1);
   return this.Y2;
};

leg.prototype.getZ2 = function(){
   this.Z2 = 0;
   return this.Z2;
};

// Inverse kinematics
leg.prototype.getTheta2 = function(){
   this.theta2 = Math.acos((this.X2*this.X2+this.Y2*this.Y2-this.L1*this.L1-this.L2*this.L2)/(2*this.L1*this.L2));
   return this.theta2;
};

leg.prototype.getTheta1 = function(){
   let b=this.L2*Math.sin(this.theta2);
   let c=this.L1+this.L2*Math.cos(this.theta2);
   this.theta1 = Math.atan2(this.X2, this.Y2)-Math.atan2(b,c);
   return this.theta1;
};

// High level API
leg.prototype.calcForwardKinematics = function(){
   this.getX1();this.getY1();this.getZ1();
   this.getX2();this.getY2();this.getZ2();
}

leg.prototype.calcInverseKinematics = function(){
   this.getTheta2(); // Mandatory order (theta2 is used to calculate theta1)
   this.getTheta1();
   this.getX1();this.getY1();this.getZ1();this.getZ2(); // Z mandatory to avoid NAN in calc
}

/* http://www.independent-software.com/determining-coordinates-on-a-html-canvas-bezier-curve.html */
leg.prototype.getBezierXY = function(t) {
   return {
     x: Math.pow(1-t,3) * this.sx + 3 * t * Math.pow(1 - t, 2) * this.c1x 
       + 3 * t * t * (1 - t) * this.c2x + t * t * t * this.ex,
     y: Math.pow(1-t,3) * this.sy + 3 * t * Math.pow(1 - t, 2) * this.c1y 
       + 3 * t * t * (1 - t) * this.c2y + t * t * t * this.ey
   }
}   

// Debug output
leg.prototype.printData = function(){
   console.log("theta1: "+Math.ceil(this.theta1*180/Math.PI)+", theta2: "+Math.ceil(this.theta2*180/Math.PI));
   console.log("X1: "+Math.ceil(this.X1)+", Y1: "+Math.ceil(this.Y1));
   console.log("X2: "+Math.ceil(this.X2)+", Y2: "+Math.ceil(this.Y2));
};

const c = document.getElementById("myCanvas");
const DRAW_FACTOR = 2;
const LEG_LENGTH = 20;
const SIDE_OFFSET_X = 200, SIDE_OFFSET_Y = 10;
const FRONT_OFFSET_X = 200, FRONT_OFFSET_Y = 150;
const LONG_LEG_DISTANCE = 25, LAT_LEG_DISTANCE = 10;
let FL_leg = new leg(LEG_LENGTH, LEG_LENGTH, 0, 0, LONG_LEG_DISTANCE, LAT_LEG_DISTANCE);
let RL_leg = new leg(LEG_LENGTH, LEG_LENGTH, 0, 0, -LONG_LEG_DISTANCE, LAT_LEG_DISTANCE);
let FR_leg = new leg(LEG_LENGTH, LEG_LENGTH, 0, 0, LONG_LEG_DISTANCE, -LAT_LEG_DISTANCE);
let RR_leg = new leg(LEG_LENGTH, LEG_LENGTH, 0, 0, -LONG_LEG_DISTANCE, -LAT_LEG_DISTANCE);
let a1 = 0, a2 = 0;
let dir = 1;
let mode = "";

function init() {
   console.log("Init");

   let md = document.getElementById("sims");
   md.value = "bezier";
   mode = "bezier";

   setInterval(loop, REFRESH);
};


function combo(thelist) {
   let idx = thelist.selectedIndex;
   mode = thelist.options[idx].innerHTML;
   a1 = 1;
}

function loop(){
   if(mode=="swipe") {
      loop_1();
   }
   else if(mode == "positions"){
      loop_2(a1);
   }
   else if(mode == "bezier"){
      loop_3(a1);
   }
}

// Angle swipe loop (forward kinematic)
function loop_1(){
   move_1();
   drawRobot();
}

// Position change (inverse kinematic)
function loop_2(step){
   if(step == 1) move_2(0, 20);
   else if(step == 2) move_2(0, 25);
   else if(step == 3) move_2(0, 30);
   else if(step == 4) move_2(0, 35);
   drawRobot();
   a1++;
   if(a1==5) a1 = 1;
}

// Bezier path (inverse kinematic)
function loop_3(step){
   move_3();
   drawRobot();
   a1+=dir;
   if((a1 == 10) || (a1 == 0)){
      dir = -dir;
      FL_leg.reversePath();
      FR_leg.reversePath();
      RL_leg.reversePath();
      RR_leg.reversePath();
   }
}

// Swipe both theta angles
function move_1(){
   // Simulate movement by using forward kinematics
   a1 += dir;
   a2 += dir;
   if(a1 == 45) dir = -1;
   else if(a1 == -45) dir = 1;

   FL_leg.setTheta1(a1*Math.PI/180);
   FL_leg.setTheta2(a2*Math.PI/180);
   FL_leg.calcForwardKinematics();
   
   RL_leg.setTheta1(a1*Math.PI/180);
   RL_leg.setTheta2(a2*Math.PI/180);
   RL_leg.calcForwardKinematics();
   
   FR_leg.setTheta1(a1*Math.PI/180);
   FR_leg.setTheta2(a2*Math.PI/180);
   FR_leg.calcForwardKinematics();
   
   RR_leg.setTheta1(a1*Math.PI/180);
   RR_leg.setTheta2(a2*Math.PI/180);
   RR_leg.calcForwardKinematics();
};

// set different positions with inverse kinematics
function move_2(x, y){
   // test inverse kenematics
   FL_leg.setTarget(x, y);
   FL_leg.calcInverseKinematics();
   
   FR_leg.setTarget(x, y);
   FR_leg.calcInverseKinematics();
   
   RL_leg.setTarget(x, y);
   RL_leg.calcInverseKinematics();
   
   RR_leg.setTarget(x, y);
   RR_leg.calcInverseKinematics();
}

function move_3(){
   FL_leg.setPath(a1/10);
   FL_leg.calcInverseKinematics();
   FR_leg.setPath(a1/10);
   FR_leg.calcInverseKinematics();
   RL_leg.setPath(a1/10);
   RL_leg.calcInverseKinematics();
   RR_leg.setPath(a1/10);
   RR_leg.calcInverseKinematics();
}

function drawLeg(context, leg){

   context.lineWidth = 1;
   context.strokeStyle = "#000000";

   // Side view
   context.beginPath();
   context.moveTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR, SIDE_OFFSET_Y);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X1*DRAW_FACTOR, SIDE_OFFSET_Y+leg.Y1*DRAW_FACTOR);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X2*DRAW_FACTOR, SIDE_OFFSET_Y+leg.Y2*DRAW_FACTOR);
   context.stroke();
   // Articulations
   context.fillStyle = "#FF0000";
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X1*DRAW_FACTOR-2, SIDE_OFFSET_Y+leg.Y1*DRAW_FACTOR-2, 5, 5);
   context.fillStyle = "#0000FF";
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X2*DRAW_FACTOR-2, SIDE_OFFSET_Y+leg.Y2*DRAW_FACTOR-2, 5, 5);

   // Front view
   context.beginPath();
   context.moveTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR, FRONT_OFFSET_Y);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z1*DRAW_FACTOR, FRONT_OFFSET_Y+leg.Y1*DRAW_FACTOR);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z2*DRAW_FACTOR, FRONT_OFFSET_Y+leg.Y2*DRAW_FACTOR);
   context.stroke();
   // Articulations
   context.fillStyle = "#FF0000";
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z1*DRAW_FACTOR-2, FRONT_OFFSET_Y+leg.Y1*DRAW_FACTOR-2, 5, 5);
   context.fillStyle = "#0000FF";
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z2*DRAW_FACTOR-2, FRONT_OFFSET_Y+leg.Y2*DRAW_FACTOR-2, 5, 5);   
}

function drawGait(ctx, leg){
   let dx = SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR;
   let dy = SIDE_OFFSET_Y;

   ctx.strokeStyle = "#888888";
   //ctx.setLineDash([5, 15]);
   ctx.lineWidth = 1;
   
   ctx.beginPath();
   ctx.moveTo(dx+leg.sx*DRAW_FACTOR, dy+leg.sy*DRAW_FACTOR);
   ctx.bezierCurveTo(dx+leg.c1x*DRAW_FACTOR, dy+leg.c1y*DRAW_FACTOR, dx+leg.c2x*DRAW_FACTOR, dy+leg.c2y*DRAW_FACTOR, dx+leg.ex*DRAW_FACTOR, dy+leg.ey*DRAW_FACTOR);
   ctx.stroke();
   ctx.beginPath();
   ctx.moveTo(dx+leg.sx*DRAW_FACTOR, dy+leg.sy*DRAW_FACTOR);
   ctx.bezierCurveTo(dx+leg.c1x*DRAW_FACTOR, dy+leg.c1y*DRAW_FACTOR, dx+leg.c2x*DRAW_FACTOR, dy+leg.c2y*DRAW_FACTOR, dx+leg.ex*DRAW_FACTOR, dy+leg.ey*DRAW_FACTOR);
   ctx.stroke();
   
   ctx.fillStyle = "#888888";
   ctx.fillRect(dx+leg.sx*DRAW_FACTOR-2, dy+leg.sy*DRAW_FACTOR-2, 5, 5);
   ctx.fillStyle = "#888888";
   ctx.fillRect(dx+leg.ex*DRAW_FACTOR-2, dy+leg.ey*DRAW_FACTOR-2, 5, 5);
   ctx.fillStyle = "#0000FF";
   ctx.fillRect(dx+leg.c1x*DRAW_FACTOR-1, dy+leg.c1y*DRAW_FACTOR-1, 3, 3);
   ctx.fillRect(dx+leg.c2x*DRAW_FACTOR-1, dy+leg.c2y*DRAW_FACTOR-1, 3, 3);
}

function drawRobot() {
   var ctx = c.getContext("2d");
   ctx.clearRect(0, 0, c.width, c.height);

   ctx.strokeStyle = "#000000";
   ctx.lineWidth = 5;

   // Draw right side view chassis
   ctx.beginPath();
   ctx.moveTo(SIDE_OFFSET_X+RR_leg.longPos*DRAW_FACTOR, SIDE_OFFSET_Y);
   ctx.lineTo(SIDE_OFFSET_X+FR_leg.longPos*DRAW_FACTOR, SIDE_OFFSET_Y);
   ctx.stroke();

   // Draw front view chassis
   ctx.beginPath();
   ctx.moveTo(FRONT_OFFSET_X+FR_leg.latPos*DRAW_FACTOR, FRONT_OFFSET_Y);
   ctx.lineTo(FRONT_OFFSET_X+FL_leg.latPos*DRAW_FACTOR, FRONT_OFFSET_Y);
   ctx.stroke();

   // Text
   ctx.font = "20px Arial";
   ctx.fillStyle = "red";
   ctx.fillText("Right view", 10, 50);
   ctx.fillText("Front view", 10, 200);

   // Write data
   ctx.font = "10px Arial";
   ctx.fillStyle = "black";
   ctx.fillText("FL: ("+Math.ceil(FL_leg.X2)+", "+Math.ceil(FL_leg.Y2)+")", 10, 250);
   ctx.fillText("RL: ("+Math.ceil(RL_leg.X2)+", "+Math.ceil(RL_leg.Y2)+")", 10, 260);
   ctx.fillText("RL: ("+Math.ceil(FR_leg.X2)+", "+Math.ceil(FR_leg.Y2)+")", 10, 270);
   ctx.fillText("RR: ("+Math.ceil(RR_leg.X2)+", "+Math.ceil(RR_leg.Y2)+")", 10, 280);

   if(mode=="bezier"){
      // Draw gait for each leg
      drawGait(ctx, FL_leg);
      drawGait(ctx, RL_leg);
      drawGait(ctx, FR_leg);
      drawGait(ctx, RR_leg);
   }

   // Draw legs
   drawLeg(ctx, FL_leg);
   drawLeg(ctx, RL_leg);
   drawLeg(ctx, FR_leg);
   drawLeg(ctx, RR_leg);
};
