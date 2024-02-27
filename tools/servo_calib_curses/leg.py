import math

# Not used. Only for init.
# positions of Bezier start and end points
SX = 10
SY = 25
EX = 0
EY = 25

#   Medium point coordinates: (X1, Y1)
#   End point coordinates:    (X2, Y2)
#   Top leg length:           L1
#   Bottom leg length:        L2 
#   Top leg angle:            theta1
#   Bottom leg angle:         theta2 
#   
#   In this module, all angles are in rad
LEG_LENGTH = 20
LONG_LEG_DISTANCE = 40
LAT_LEG_DISTANCE = 10
DEBUG = 0

class leg:
    def __init__(self, name, L1, L2, theta1, theta2, theta3, longPos, latPos):
        self.name = name
        self.L1 = L1
        self.L2 = L2
        self.X1 = 0 # not in original js code
        self.X2 = 0
        self.Y1 = 0 # not in original js code
        self.Y2 = 0
        self.Z1 = 0 # not in original js code
        self.Z2 = 0
        self.theta1 = theta1
        self.theta2 = theta2
        self.theta3 = theta3
        self.longPos = longPos
        self.latPos = latPos
        self.direction = 1
        self.DX, self.DY, self.DZ = 0.1, 0.1, 0.1

        # recalculate bezier curve
        self.sx = SX # x coordinate of bezier start point
        self.sy = SY # y coordinate of bezier start point
        self.c1x = self.sx # x coordinate of bezier control point 1
        self.c1y = self.sy + 5 * self.direction # y coordinate of bezier control point 1
        self.ex = EX # x coordinate of bezier end point
        self.ey = EY # y coordinate of bezier end point
        self.c2x = self.ex # x coordinate of bezier control point 2
        self.c2y = self.ey + 5 * self.direction # y coordinate of bezier control point 2

        if DEBUG:
            self.f = open("debugdata.log", "a")

    def debug(self, text):
        if "FL" in self.name and DEBUG:
            self.f.write(self.name+" - "+text+"\n")

    def setTheta1(self, angle):
        self.theta1 = angle

    def setTheta2(self, angle):
        self.theta2 = angle

    def setTheta3(self, angle):
        self.theta3 = angle

    def setTarget(self, x, y, z):
        self.X2 = x
        self.Y2 = y
        self.Z2 = z

    def setTargetAngles(self, theta1, theta2, theta3):
        self.theta1 = theta1
        self.theta2 = theta2
        self.theta3 = theta3

    def setPath(self, t):
        vals = self.getBezierXY(t)
        self.X2 = vals['x']
        self.Y2 = vals['y']
        self.debug("Bezier: "+str(vals)+" - pos: "+str(t))

    def setSpeeds(self, dx, dy, dz):
        self.DX = dx
        self.DY = dy
        self.DZ = dz

    # recalculate bezier curve. Start and end are equal in both directions-
    # only control point is varying in both directions
    def reversePath(self):
        self.direction = -self.direction
        #self.sx = SX
        #self.sy = SY
        self.c1x = self.sx
        self.c1y = self.sy + 5 * self.direction
        #self.ex = EX
        #self.ey = EY
        self.c2x = self.ex
        self.c2y = self.ey + 5 * self.direction

    def calcX1(self):
        self.X1 = self.L1 * math.sin(self.theta1)
        return self.X1

    def calcY1(self):
        self.Y1 = self.L1 * math.cos(self.theta1)
        return self.Y1

    def calcZ1(self):
        self.Z1 = 0
        return self.Z1

    def calcX2(self):
        self.X2 = self.L2 * math.cos(math.pi/2 - self.theta1 - self.theta2) + self.L1 * math.sin(self.theta1)
        return self.X2

    def calcY2(self):
        self.Y2 = self.L2 * math.sin(math.pi/2 - self.theta1 - self.theta2) + self.L1 * math.cos(self.theta1)
        return self.Y2

    def calcZ2(self):
        return self.Z2

    def calcTheta2(self):
        self.theta2 = math.acos((self.X2 * self.X2 + self.Y2 * self.Y2 - self.L1 * self.L1 - self.L2 * self.L2) / (2 * self.L1 * self.L2))
        return self.theta2

    def calcTheta1(self):
        b = self.L2 * math.sin(self.theta2)
        c = self.L1 + self.L2 * math.cos(self.theta2)
        self.theta1 = math.atan2(self.X2, self.Y2) - math.atan2(b, c)
        return self.theta1

    def calcTheta3(self):
        # only for manual control
        return self.theta3

    def calcForwardKinematics(self):
        self.calcX1()
        self.calcY1()
        self.calcZ1()
        self.calcX2()
        self.calcY2()
        self.calcZ2()

    def calcInverseKinematics(self):
        self.calcTheta2()  # Mandatory order (theta2 is used to calculate theta1)
        self.calcTheta1()
        # Calculate intermediate joint
        self.calcX1()
        self.calcY1()
        self.calcZ1()
        self.calcZ2()  # Z mandatory to avoid NAN in calc

# get coordinates of point on Bezier curve.
# t determines how far we are on the curve. 0: Start, 1: End
    def getBezierXY(self, t):
        return {
            'x': math.pow(1 - t, 3) * self.sx + 3 * t * math.pow(1 - t, 2) * self.c1x +
                 3 * t * t * (1 - t) * self.c2x + t * t * t * self.ex,
            'y': math.pow(1 - t, 3) * self.sy + 3 * t * math.pow(1 - t, 2) * self.c1y +
                 3 * t * t * (1 - t) * self.c2y + t * t * t * self.ey
        }
                                               
    def printData(self):
        return f"theta1: {math.ceil(self.theta1 * 180 / math.pi):03d}°, \
theta2: {math.ceil(self.theta2 * 180 / math.pi):03d}°, \
theta3: {math.ceil(self.theta3 * 180 / math.pi):03d}°, \
P1({math.ceil(self.X1)}, {math.ceil(self.Y1)}, {math.ceil(self.Z1)}), \
P2({math.ceil(self.X2)}, {math.ceil(self.Y2)}, {math.ceil(self.Z2)})"
        
    def move_next(self, target_x, target_y, target_z):
        x, y, z, dx, dy, dz = 0, 0, 0, 0, 0, 0
        x = self.X2
        y = self.Y2
        z = self.Z2

        if x < target_x:
            if (target_x - x) > self.DX:
                dx = self.DX
            else:
                dx = target_x - x
        elif x > target_x:
            if (x - target_x) >= self.DX:
                dx = -self.DX
            else:
                dx = -(x - target_x)

        if y < target_y:
            if (target_y - y) > self.DY:
                dy = self.DY
            else:
                dy = target_y - y
        elif y > target_y:
            if (y - target_y) >= self.DY:
                dy = -self.DY
            else:
                dy = -(y - target_y)

        if z < target_z:
            if (target_z - z) > self.DZ:
                dz = self.DZ
            else:
                dz = target_z - z
        elif z > target_z:
            if (z - target_z) >= self.DZ:
                dz = -self.DZ
            else:
                dz = -(z - target_z)

        if dx != 0 or dy != 0 or dz != 0:
            self.setTarget(x + dx, y + dy, z + dz)
            self.calcInverseKinematics()


# Run this if standalone (test purpose)
if __name__ == '__main__':
    
    FL_leg = leg("FL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2)
    RL_leg = leg("RL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2)
    #FR_leg = leg("FR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2)
    #RR_leg = leg("RR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2)

    FL_leg.printData()
    print("Stand-up")
    for i in range(16):
        FL_leg.move_next(0, 16, 0)
        RL_leg.move_next(0, 16, 0)
        print(FL_leg.printData())
    print("Bezier 1 FL leg")
    FL_leg.sx = FL_leg.X2
    FL_leg.sy = FL_leg.Y2
    RL_leg.sx = RL_leg.X2
    RL_leg.sy = RL_leg.Y2
    
    FL_leg.ex = FL_leg.X2-5
    FL_leg.ey = FL_leg.Y2
    RL_leg.ex = RL_leg.X2-5
    RL_leg.ey = RL_leg.Y2
    for i in range(11):
        FL_leg.setPath(i/10)
        FL_leg.calcInverseKinematics()
        print(FL_leg.printData())
    print("Reverse RL leg")
    RL_leg.reversePath()
    for i in reversed(range(11)):
        RL_leg.setPath(i/10)
        RL_leg.calcInverseKinematics()
        print(RL_leg.printData())
