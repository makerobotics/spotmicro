/* Medium point coordinates: (X1, Y1)
   End point coordinates:    (X2, Y2)
   Top leg length:           L1
   Bottom leg length:        L2 
   Top leg angle:            theta1
   Bottom leg angle:         theta2 */
   
function leg(L1, L2, theta1, theta2){
   this.L1 = L1;
   this.L2 = L2;
   this.theta1 = theta1;
   this.theta2 = theta2;
};

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

leg.prototype.getX2 = function(){
   this.X2 = this.L2*Math.cos(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.sin(this.theta1);
   return this.X2;
};

leg.prototype.getY2 = function(){
   this.Y2 = this.L2*Math.sin(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.cos(this.theta1);
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
let FL_leg = new leg(20, 20, 0, 0);
let a1 = 0, a2 = 0;

function init() {
   console.log("Init");

   FL_leg.setTheta1(0);
   FL_leg.setTheta2(0);

   setInterval(drawRobot, 1000);
}

function move(){
   a1 ++;
   a2 ++;
   FL_leg.setTheta1(a1*Math.PI/180);
   FL_leg.setTheta2(a2*Math.PI/180);
}

function drawRobot() {
   let ctx = c.getContext("2d");
   ctx.clearRect(0, 0, c.width, c.height);
   FL_leg.printData();

   ctx.moveTo(0, 0);
   ctx.lineTo(FL_leg.getX1()*10, FL_leg.getY1()*10);
   ctx.lineTo(FL_leg.getX2()*10, FL_leg.getY2()*10);
   ctx.stroke();
   move();
}
