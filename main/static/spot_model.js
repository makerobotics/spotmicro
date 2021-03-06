const SX = 10;
const SY = 25;
const EX = 0;
const EY = 25;

/* Medium point coordinates: (X1, Y1)
   End point coordinates:    (X2, Y2)
   Top leg length:           L1
   Bottom leg length:        L2 
   Top leg angle:            theta1
   Bottom leg angle:         theta2 
   
   In this module, all angles are in rad
*/
function leg(name, L1, L2, theta1, theta2, theta3, longPos, latPos){
   this.name = name;
   this.L1 = L1;
   this.L2 = L2;
   this.X2 = 0;
   this.Y2 = 0;
   this.Z2 = 0;
   this.theta1 = theta1;
   this.theta2 = theta2;
   this.theta3 = theta3;
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

leg.prototype.setTheta3 = function(angle){
   this.theta3 = angle;
};

leg.prototype.setTarget = function(x, y, z){
   this.X2 = x;
   this.Y2 = y;
   this.Z2 = z;
}

leg.prototype.setTargetAngles = function(theta1, theta2, theta3){
   this.theta1 = theta1;
   this.theta2 = theta2;
   this.theta3 = theta3;
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
leg.prototype.calcX1 = function(){
   this.X1 = this.L1*Math.sin(this.theta1);
   return this.X1;
};

leg.prototype.calcY1 = function(){
   this.Y1 = this.L1*Math.cos(this.theta1);
   return this.Y1;
};

leg.prototype.calcZ1 = function(){
   this.Z1 = 0;
   return this.Z1;
};

leg.prototype.calcX2 = function(){
   this.X2 = this.L2*Math.cos(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.sin(this.theta1);
   return this.X2;
};

leg.prototype.calcY2 = function(){
   this.Y2 = this.L2*Math.sin(Math.PI/2-this.theta1-this.theta2)+this.L1*Math.cos(this.theta1);
   return this.Y2;
};

leg.prototype.calcZ2 = function(){
   return this.Z2;
};

// Inverse kinematics
leg.prototype.calcTheta2 = function(){
   this.theta2 = Math.acos((this.X2*this.X2+this.Y2*this.Y2-this.L1*this.L1-this.L2*this.L2)/(2*this.L1*this.L2));
   return this.theta2;
};

leg.prototype.calcTheta1 = function(){
   let b=this.L2*Math.sin(this.theta2);
   let c=this.L1+this.L2*Math.cos(this.theta2);
   this.theta1 = Math.atan2(this.X2, this.Y2)-Math.atan2(b,c);
   return this.theta1;
};

leg.prototype.calcTheta3 = function(){
   // only for manual control
   return this.theta3;
};

// High level API: get the joint positions out of the angles
leg.prototype.calcForwardKinematics = function(){
   this.calcX1();this.calcY1();this.calcZ1();
   this.calcX2();this.calcY2();this.calcZ2();
}

// High level API: get the servo angles out of the joint positions
leg.prototype.calcInverseKinematics = function(){
   this.calcTheta2(); // Mandatory order (theta2 is used to calculate theta1)
   this.calcTheta1();
   // Calculate intermediate joint
   this.calcX1();this.calcY1();this.calcZ1();this.calcZ2(); // Z mandatory to avoid NAN in calc
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
   console.log("theta1: "+Math.ceil(this.theta1*180/Math.PI)+", theta2: "+Math.ceil(this.theta2*180/Math.PI)+", theta3: "+Math.ceil(this.theta3*180/Math.PI));
   console.log("X1: "+Math.ceil(this.X1)+", Y1: "+Math.ceil(this.Y1));
   console.log("X2: "+Math.ceil(this.X2)+", Y2: "+Math.ceil(this.Y2));
};
