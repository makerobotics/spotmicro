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

// Output
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

function init() {
   console.log("Init");

   FL_leg.setTheta1(0);
   FL_leg.setTheta2(0);

   // move_1: move servo angles coninuously
//   setInterval(loop, TIME_INTERVAL);

   // move_2: move FL leg to 4 points (IK) in a square
   setTimeout(loop_2, 1000);
   a1 = 1;
   setInterval(function() {
      loop_2(a1);
   }, 1500)
   //move_2(0, 20);
   //drawRobot();
};

function loop(){
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
   FL_leg.getX1();FL_leg.getY1();FL_leg.getZ1();
   FL_leg.getX2();FL_leg.getY2();FL_leg.getZ2();
   
   RL_leg.setTheta1(a1*Math.PI/180);
   RL_leg.setTheta2(a2*Math.PI/180);
   RL_leg.getX1();RL_leg.getY1();RL_leg.getZ1();
   RL_leg.getX2();RL_leg.getY2();RL_leg.getZ2();
   
   FR_leg.setTheta1(a1*Math.PI/180);
   FR_leg.setTheta2(a2*Math.PI/180);
   FR_leg.getX1();FR_leg.getY1();FR_leg.getZ1();
   FR_leg.getX2();FR_leg.getY2();FR_leg.getZ2();
   
   RR_leg.setTheta1(a1*Math.PI/180);
   RR_leg.setTheta2(a2*Math.PI/180);
   RR_leg.getX1();RR_leg.getY1();RR_leg.getZ1();
   RR_leg.getX2();RR_leg.getY2();RR_leg.getZ2();
};

function move_2(x, y){
   // test inverse kenematics
   FL_leg.setTarget(x, y);
   FL_leg.getTheta2();
   FL_leg.getTheta1();
   FL_leg.getX1();FL_leg.getY1();FL_leg.getZ1();
   //console.log(FL_leg.X1, FL_leg.Y1, FL_leg.Z1);
   FL_leg.printData();
}

function drawLeg(context, leg){
   context.beginPath();
   context.moveTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR, SIDE_OFFSET_Y);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X1*DRAW_FACTOR, SIDE_OFFSET_Y+leg.Y1*DRAW_FACTOR);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X2*DRAW_FACTOR, SIDE_OFFSET_Y+leg.Y2*DRAW_FACTOR);
   context.stroke();
   context.fillStyle = "#FF0000";
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X1*DRAW_FACTOR-1, SIDE_OFFSET_Y+leg.Y1*DRAW_FACTOR-1, 3, 3);
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.X2*DRAW_FACTOR-1, SIDE_OFFSET_Y+leg.Y2*DRAW_FACTOR-1, 3, 3);

   context.beginPath();
   context.moveTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR, FRONT_OFFSET_Y);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z1*DRAW_FACTOR, FRONT_OFFSET_Y+leg.Y1*DRAW_FACTOR);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z2*DRAW_FACTOR, FRONT_OFFSET_Y+leg.Y2*DRAW_FACTOR);
   context.stroke();
   context.fillStyle = "#0000FF";
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z1*DRAW_FACTOR-1, FRONT_OFFSET_Y+leg.Y1*DRAW_FACTOR-1, 3, 3);
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.Z2*DRAW_FACTOR-1, FRONT_OFFSET_Y+leg.Y2*DRAW_FACTOR-1, 3, 3);
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
   
   // Draw legs
   drawLeg(ctx, FL_leg);
   drawLeg(ctx, RL_leg);
   drawLeg(ctx, FR_leg);
   drawLeg(ctx, RR_leg);
};
