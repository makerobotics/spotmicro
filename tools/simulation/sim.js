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
   //console.log(this.X2, this.Y2);
   this.theta2 = Math.acos((this.X2*this.X2+this.Y2*this.Y2-this.L1*this.L1-this.L2*this.L2)/(2*this.L1*this.L2));
   //console.log(this.theta2*180/Math.PI,this.theta2);
   return this.theta2;
};

leg.prototype.getTheta1 = function(){
   let b=this.L2*Math.sin(this.theta2);
   let c=this.L1+this.L2*Math.cos(this.theta2);
   this.theta1 = Math.atan2(this.X2, this.Y2)-Math.atan2(b,c);
   return this.theta1;
};

leg.prototype.calcForwardKinematics = function(){
   this.getX1();this.getY1();this.getZ1();
   this.getX2();this.getY2();this.getZ2();
}

leg.prototype.calcInverseKinematics = function(){
   this.getTheta2(); // Mandatory order (theta2 is used to calculate theta1)
   this.getTheta1();
   this.getX1();this.getY1();this.getZ1();this.getZ2(); // Z mandatory to avoid NAN in calc
}

// Debug output
leg.prototype.printData = function(){
   console.log("theta1: "+Math.ceil(this.theta1*180/Math.PI)+", theta2: "+Math.ceil(this.theta2*180/Math.PI));
   console.log("X1: "+Math.ceil(this.X1)+", Y1: "+Math.ceil(this.Y1));
   console.log("X2: "+Math.ceil(this.X2)+", Y2: "+Math.ceil(this.Y2));
};

const c = document.getElementById("myCanvas");
const DRAW_FACTOR = 2;
const TIME_INTERVAL = 20;
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

/* http://www.independent-software.com/determining-coordinates-on-a-html-canvas-bezier-curve.html */
function getBezierXY(t, sx, sy, cp1x, cp1y, cp2x, cp2y, ex, ey) {
   return {
     x: Math.pow(1-t,3) * sx + 3 * t * Math.pow(1 - t, 2) * cp1x 
       + 3 * t * t * (1 - t) * cp2x + t * t * t * ex,
     y: Math.pow(1-t,3) * sy + 3 * t * Math.pow(1 - t, 2) * cp1y 
       + 3 * t * t * (1 - t) * cp2y + t * t * t * ey
   };
 }

function init() {
   console.log("Init");
   let md = document.getElementById("sims");
   md.value = "";

   FL_leg.setTheta1(0);
   FL_leg.setTheta2(0);

   // move_1: move servo angles coninuously
//   setInterval(loop_1, TIME_INTERVAL);

   // move_2: move FL leg to 4 points (IK) in a square
/*   a1 = 1;
   setInterval(function() {
      loop_2(a1);
   }, 1500)*/

   setInterval(loop, 1000);
};


function combo(thelist) {
   let idx = thelist.selectedIndex;
   mode = thelist.options[idx].innerHTML;
   //console.log("Selected: "+mode);
   a1 = 1;
}

function loop(){
   //console.log("Selected: "+mode);
   if(mode=="swipe") {
      loop_1();
   }
   else if(mode == "positions"){
      loop_2(a1);
   }
}

function loop_1(){
   move_1();
   drawRobot();
}

function loop_2(step){
   if(step == 1) move_2(0, 20);
   else if(step == 2) move_2(0, 25);
   else if(step == 3) move_2(0, 30);
   else if(step == 4) move_2(0, 35);
   drawRobot();
   a1++;
   if(a1==5) a1 = 1;
}

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

function drawLeg(context, leg){

   // Side view
   context.beginPath();
   context.moveTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR, SIDE_OFFSET_Y);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X1*DRAW_FACTOR, SIDE_OFFSET_Y+leg.Y1*DRAW_FACTOR);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X2*DRAW_FACTOR, SIDE_OFFSET_Y+leg.Y2*DRAW_FACTOR);
   context.stroke();
   // Articulations
   context.fillStyle = "#FF0000";
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X1*DRAW_FACTOR-1, SIDE_OFFSET_Y+leg.Y1*DRAW_FACTOR-1, 3, 3);
   context.fillStyle = "#0000FF";
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X2*DRAW_FACTOR-1, SIDE_OFFSET_Y+leg.Y2*DRAW_FACTOR-1, 3, 3);

   // Front view
   context.beginPath();
   context.moveTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR, FRONT_OFFSET_Y);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z1*DRAW_FACTOR, FRONT_OFFSET_Y+leg.Y1*DRAW_FACTOR);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z2*DRAW_FACTOR, FRONT_OFFSET_Y+leg.Y2*DRAW_FACTOR);
   context.stroke();
   // Articulations
   context.fillStyle = "#FF0000";
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z1*DRAW_FACTOR-1, FRONT_OFFSET_Y+leg.Y1*DRAW_FACTOR-1, 3, 3);
   context.fillStyle = "#0000FF";
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z2*DRAW_FACTOR-1, FRONT_OFFSET_Y+leg.Y2*DRAW_FACTOR-1, 3, 3);   
}

function drawGait(ctx, leg){
   let sx, sy, c1x, c1y, c2x, c2y, ex, ey;
   
   sx = SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR-10;
   sy = SIDE_OFFSET_Y-10;
   c1x = sx;
   c1y = sx;
   c2x = sx;
   c2y = sx;
   ex = SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+10;
   ey = SIDE_OFFSET_Y+10;
   
   ctx.beginPath();
   ctx.moveTo(20, 20);
   //ctx.bezierCurveTo(20, 100, 200, 100, 200, 20);
   ctx.bezierCurveTo(c1x, c1y, c2x, c2y, ex, ey);
   getBezierXY(0.5, sx, sy, c1x, c1y, c2x, c2y, ex, ey);
   ctx.stroke(); 
}

function drawRobot() {
   var ctx = c.getContext("2d");
   ctx.clearRect(0, 0, c.width, c.height);

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

   // Draw gait for each leg
   drawGait(ctx, FL_leg);

   // Draw legs
   drawLeg(ctx, FL_leg);
   drawLeg(ctx, RL_leg);
   drawLeg(ctx, FR_leg);
   drawLeg(ctx, RR_leg);
};
