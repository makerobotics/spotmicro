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
   this.Y1 = 0;
   return this.Y1;
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
   this.Y2 = 0;
   return this.Y2;
};

// Inverse kinematics
leg.prototype.getTheta1 = function(){
   return this.L2*Math.cos(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.sin(this.theta1);
};

leg.prototype.getTheta2 = function(){
   return this.L2*Math.cos(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.sin(this.theta1);
};

// Output
leg.prototype.printData = function(){
   console.log("Hip angle: "+Math.ceil(this.theta1*180/Math.PI)+", Wrist angle: "+Math.ceil(this.theta2*180/Math.PI));
   console.log("X1: "+Math.ceil(this.getX1())+", Y1: "+Math.ceil(this.getY1()));
   console.log("X2: "+Math.ceil(this.getX2())+", Y2: "+Math.ceil(this.getY2()));
};

const c = document.getElementById("myCanvas");
const DRAW_FACTOR = 2;
const TIME_INTERVAL = 20;
const LEG_LENGTH = 20;
const SIDE_OFFSET_X = 200, SIDE_OFFSET_Y = 10;
const FRONT_OFFSET_X = 200, FRONT_OFFSET_Y = 150;
const LONG_LEG_DISTANCE = 25, LAT_LEG_DISTANCE = 10;
let FL_leg = new leg(LEG_LENGTH, LEG_LENGTH, 0, 0, LONG_LEG_DISTANCE, LAT_LEG_DISTANCE);
let RL_leg = new leg(LEG_LENGTH, LEG_LENGTH, 10, 10, -LONG_LEG_DISTANCE, LAT_LEG_DISTANCE);
let FR_leg = new leg(LEG_LENGTH, LEG_LENGTH, 20, 20, LONG_LEG_DISTANCE, -LAT_LEG_DISTANCE);
let RR_leg = new leg(LEG_LENGTH, LEG_LENGTH, 30, 30, -LONG_LEG_DISTANCE, -LAT_LEG_DISTANCE);
let a1 = 0, a2 = 0;
let dir = 1;

function init() {
   console.log("Init");

   FL_leg.setTheta1(0);
   FL_leg.setTheta2(0);

   setInterval(drawRobot, TIME_INTERVAL);
};

function move(){
   // Simulate movement by using forward kinematics
   a1 += dir;
   a2 += dir;
   if(a1 == 45) dir = -1;
   else if(a1 == -45) dir = 1;

   FL_leg.setTheta1(a1*Math.PI/180);
   FL_leg.setTheta2(a2*Math.PI/180);
   RL_leg.setTheta1(a1*Math.PI/180);
   RL_leg.setTheta2(a2*Math.PI/180);
   FR_leg.setTheta1(a1*Math.PI/180);
   FR_leg.setTheta2(a2*Math.PI/180);
   RR_leg.setTheta1(a1*Math.PI/180);
   RR_leg.setTheta2(a2*Math.PI/180);
};

function drawLeg(context, leg){
   context.beginPath();
   context.moveTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR, SIDE_OFFSET_Y);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.getX1()*DRAW_FACTOR, SIDE_OFFSET_Y+leg.getY1()*DRAW_FACTOR);
   context.lineTo(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.getX2()*DRAW_FACTOR, SIDE_OFFSET_Y+leg.getY2()*DRAW_FACTOR);
   context.stroke();
   context.fillStyle = "#FF0000";
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.getX1()*DRAW_FACTOR-1, SIDE_OFFSET_Y+leg.getY1()*DRAW_FACTOR-1, 3, 3);
   context.fillRect(SIDE_OFFSET_X+leg.longPos*DRAW_FACTOR+leg.getX2()*DRAW_FACTOR-1, SIDE_OFFSET_Y+leg.getY2()*DRAW_FACTOR-1, 3, 3);

   context.beginPath();
   context.moveTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR, FRONT_OFFSET_Y);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.getZ1()*DRAW_FACTOR, FRONT_OFFSET_Y+leg.getY1()*DRAW_FACTOR);
   context.lineTo(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.getZ2()*DRAW_FACTOR, FRONT_OFFSET_Y+leg.getY2()*DRAW_FACTOR);
   context.stroke();
   context.fillStyle = "#0000FF";
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.getZ1()*DRAW_FACTOR-1, FRONT_OFFSET_Y+leg.getY1()*DRAW_FACTOR-1, 3, 3);
   context.fillRect(FRONT_OFFSET_X+leg.latPos*DRAW_FACTOR+leg.getZ2()*DRAW_FACTOR-1, FRONT_OFFSET_Y+leg.getY2()*DRAW_FACTOR-1, 3, 3);
}

function drawRobot() {
   var ctx = c.getContext("2d");
   ctx.clearRect(0, 0, c.width, c.height);
   //FL_leg.printData();

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

   move();
};
