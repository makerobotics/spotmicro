import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from leg import leg

LEG_LENGTH = 20
LONG_LEG_DISTANCE = 40
LAT_LEG_DISTANCE = 10

#todo: to be removed
class Walking_Leg:
    def __init__(self, name, x, y, z) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.height = z
        self.UP = 5
        self.FWD_REV = 5
        self.phase = 0

    def run(self, speed):
        trigger = 0
        SPEED_FACTOR = 3
        match self.phase:
            # Move up
            case 0:
                self.z += speed*SPEED_FACTOR
                trigger = 1
                if self.z >= (self.height+self.UP):
                    self.phase += 1
                    trigger = 2
            # Move forward
            case 1:
                self.x += speed*SPEED_FACTOR
                trigger = 3
                if self.x >= self.FWD_REV:
                    self.phase += 1
                    trigger = 4
            # Move down
            case 2:
                self.z -= speed*SPEED_FACTOR
                trigger = 5
                if self.z <= self.height:
                    self.phase += 1
                    trigger = 6
            # Move backward and get traction
            case 3:
                self.x -= speed
                trigger_distance = 2*self.FWD_REV/3
                if self.FWD_REV-trigger_distance-speed/2 <= self.x <= self.FWD_REV-trigger_distance+speed/2:
                    trigger = 71
                    print(f"{self.FWD_REV-trigger_distance-speed/2:2.1f} < {self.x:2.1f} < {self.FWD_REV-trigger_distance+speed/2:2.1f}")
                elif self.FWD_REV-2*trigger_distance-speed/2 <= self.x <= self.FWD_REV-2*trigger_distance+speed/2:
                    trigger = 72
                    print(f"{self.FWD_REV-2*trigger_distance-speed/2:2.1f} < {self.x:2.1f} < {self.FWD_REV-2*trigger_distance+speed/2:2.1f}")
                elif self.x <= -self.FWD_REV:
                    self.phase = 0
                    trigger = 73
                else:
                    trigger = 70
            case _:
                print("Unexpected phase!")
        if "RL" in self.name:
            print(f"Leg {self.name} in phase {self.phase:d},{trigger:d} at ({self.x:2.1f}, {self.y:2.1f}, {self.z:2.1f})")
        return trigger
    
class Walking:
    def __init__(self):
        self.UP = 5
        self.FWD = 5

        self.leg_FL = leg("FL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2)
        self.leg_RL = leg("RL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2)
        self.leg_FR = leg("FR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2)
        self.leg_RR = leg("RR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2)

        self.phase = 0

    def prepare_for_gait(self, speed):
        match self.phase:
            case 0:
                if self.leg_RL.prepare_leg_position(speed, -5) == 3:
                    self.phase += 1
                    print("end of RL")
            case 1:
                if self.leg_FL.prepare_leg_position(speed, -2) == 3:
                    self.phase += 1
                    print("end of FL")
            case 2:
                if self.leg_FR.prepare_leg_position(speed, 2) == 3:
                    self.phase += 1
                    print("end of FR")
            case 3:
                if self.leg_RR.prepare_leg_position(speed, 5) == 3:
                    self.phase += 1
                    print("end of RR")
        return self.phase

    def gait(self, speed):
        self.leg_FL.walk(speed)
        self.leg_RL.walk(speed)
        self.leg_RR.walk(speed)
        self.leg_FR.walk(speed)

class DynamicThreeDPlotter:
    def __init__(self, legs, knees, FRAMES):
        self.legs = legs
        self.knees = knees
        self.counter = 0
        self.frames = FRAMES
        # Create a 3D axis
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        # Initialize scatter plot for points
        self.points_scatter = self.ax.scatter([], [], [], c='red', marker='o', label='Points')
        # Initialize line plot for lines
        self.lines_plot, = self.ax.plot([], [], [], c='blue', label='Lines')
        
        self.legplots1 = [self.ax.plot([], [], [], lw=1, c='red')[0] for _ in range(4)]
        self.legplots2 = [self.ax.plot([], [], [], lw=1, c='green')[0] for _ in range(4)]

    def plot_static_frame(self):
        # Legs:                 FR           FL          RR           RL
        static_points_data = [(20, -5, 0), (20, 5, 0), (-20, 5, 0), (-20, -5, 0)]
        # Clear existing points
        self.points_scatter.remove()
        # Assign colors to feet
        feet_colors = ['green', 'red', 'blue', 'blue']
        # Plot points
        x, y, z = zip(*static_points_data)
#        self.points_scatter = self.ax.scatter(x, y, z, c='red', marker='o', label='Points')
        self.points_scatter = self.ax.scatter(x, y, z, c=feet_colors, marker='o', label='Points')

        # Update lines data
        new_points_data = [(x, y, z) for x, y, z in static_points_data]
        new_lines_data = [(new_points_data[i], new_points_data[i+1]) for i in range(len(new_points_data)-1)]
        new_lines_data.append((new_points_data[0], new_points_data[3]))
        # Clear existing lines
        self.lines_plot.remove()
        # Plot lines
        x_lines, y_lines, z_lines = zip(*sum(new_lines_data, ()))
        self.lines_plot, = self.ax.plot(x_lines, y_lines, z_lines, c='blue', label='Lines')

    def plot_points(self, frame):
        # Legs:                 FR           FL          RR           RL
        static_points_data = [(20, -5, 0), (20, 5, 0), (-20, -5, 0), (-20, 5, 0)]
        
        new_points_data = []
        for i in range(4):
            # calculate feet points
            new_points_data.append((static_points_data[i][0]+self.legs[self.counter][i][0],
                                 static_points_data[i][1]+self.legs[self.counter][i][1],
                                 static_points_data[i][2]+self.legs[self.counter][i][2]))
            # calculate knee points
            new_points_data.append((static_points_data[i][0]+self.knees[self.counter][i][0],
                                 static_points_data[i][1]+self.knees[self.counter][i][1],
                                 static_points_data[i][2]+self.knees[self.counter][i][2]))
            # calculate top lines
            x1, y1, z1 = [static_points_data[i][0], static_points_data[i][0]+self.knees[self.counter][i][0]], \
            [static_points_data[i][1], static_points_data[i][1]+self.knees[self.counter][i][1]], \
            [static_points_data[i][2], static_points_data[i][2]+self.knees[self.counter][i][2]] 
            # calculate bottom lines
            x2, y2, z2 = [static_points_data[i][0]+self.knees[self.counter][i][0], static_points_data[i][0]+self.legs[self.counter][i][0]], \
            [static_points_data[i][1]+self.knees[self.counter][i][1], static_points_data[i][1]+self.legs[self.counter][i][1]], \
            [static_points_data[i][2]+self.knees[self.counter][i][2], static_points_data[i][2]+self.legs[self.counter][i][2]] 
            # Draw the legs
            self.legplots1[i].set_data_3d(x1, y1, z1)
            self.legplots2[i].set_data_3d(x2, y2, z2)
            
        self.counter += 1
        if self.counter == self.frames:
            self.counter = 0

        # Clear existing points
        self.points_scatter.remove()
        # Plot points
        x, y, z = zip(*new_points_data)
        self.points_scatter = self.ax.scatter(x, y, z, c='green', marker='o', label='Points')

    def set_labels(self, xlabel, ylabel, zlabel):
        # Set labels
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_zlabel(zlabel)

        self.ax.set_xlim([-30, 30])
        self.ax.set_ylim([-30, 30])
        self.ax.set_zlim([-30, 30])

    def add_legend(self):
        # Add a legend
        self.ax.legend()
    def show_plot(self):
        # Show the plot
        plt.show()

    def animate(self, frames=100, interval=100):
        # Create animation
        animation = FuncAnimation(self.fig, self.update_plot, frames=frames, interval=interval, blit=False)

        # Show the animation
        plt.show()

    def update_plot(self, frame):
        self.plot_static_frame()
        self.plot_points(frame)
        

# Run this if standalone (test purpose)
if __name__ == '__main__':
    legs = []
    knees = []
    parameters = []
    phase = 0
    FRAMES = 100
    w = Walking()
    print("Stand-up -20 for walk")
    while not w.leg_FL.move_next(0, 0, -20):
        w.leg_RL.move_next(0, 0, -20)
        w.leg_FR.move_next(0, 0, -20)
        w.leg_RR.move_next(0, 0, -20)
    print(w.leg_FL.printData())
    print(w.leg_FR.printData())
    print(w.leg_RL.printData())
    print(w.leg_RR.printData())
    print("Walk for n ticks")
    for i in range(FRAMES):
        match phase:
            case 0:
                if w.prepare_for_gait(1.0)>=4:
                    phase += 1
                    print("Preparation completed")
            case 1:
                w.leg_FL.phase = 0
                w.leg_FR.phase = 0
                w.leg_RL.phase = 0
                w.leg_RR.phase = 0
                phase += 1
            case 2:
                w.gait(0.5)
        print(w.leg_FL.printData())
        print(w.leg_FR.printData())
        print(w.leg_RL.printData())
        print(w.leg_RR.printData())
        legs.append([(w.leg_FR.X2, w.leg_FR.Y2, w.leg_FR.Z2),
                     (w.leg_FL.X2, w.leg_FL.Y2, w.leg_FL.Z2),
                     (w.leg_RR.X2, w.leg_RR.Y2, w.leg_RR.Z2),
                     (w.leg_RL.X2, w.leg_RL.Y2, w.leg_RL.Z2)])
        knees.append([(w.leg_FR.X1, w.leg_FR.Y1, w.leg_FR.Z1),
                     (w.leg_FL.X1, w.leg_FL.Y1, w.leg_FL.Z1),
                     (w.leg_RR.X1, w.leg_RR.Y1, w.leg_RR.Z1),
                     (w.leg_RL.X1, w.leg_RL.Y1, w.leg_RL.Z1)])
        #parameters.append((w.leg_FL.X1, w.leg_FL.X2, w.leg_FL.Z1, w.leg_FL.Z2, w.leg_FL.theta1, w.leg_FL.theta2))
        #parameters.append((w.leg_FL.X2, w.leg_FL.Z2, w.leg_FL.theta1, w.leg_FL.theta2))
        #parameters.append((w.leg_FL.X2, w.leg_FR.X2, w.leg_RL.X2, w.leg_RR.X2))
        #parameters.append((w.leg_RL.X2, w.leg_FL.X2, w.leg_RL.Z2, w.leg_FL.Z2))
        parameters.append((w.leg_FL.X2, w.leg_FR.X2, w.leg_RL.X2, w.leg_RR.X2, w.leg_FL.trigger, w.leg_FR.trigger, w.leg_RL.trigger, w.leg_RR.trigger))

    # 3D dynamic view
    if 1:
        # Create an instance of the DynamicThreeDPlotter class
        dynamic_plotter = DynamicThreeDPlotter(legs, knees, FRAMES)

        # Customize the plot
        dynamic_plotter.set_labels('X-axis', 'Y-axis', 'Z-axis')
        dynamic_plotter.add_legend()

        # Animate the plot
        dynamic_plotter.animate(frames=FRAMES, interval=20)

    # 2D charts
    if 0:
        #plt.plot(parameters, ',-', label=['X1', 'X2', 'Z1', 'Z2', 'theta1', 'theta2'])
        #plt.plot(parameters, ',-', label=['X2', 'Z2', 'theta1', 'theta2'])
        plt.plot(parameters, ',-', drawstyle='steps', label=['X2(FL)', 'X2(FR)', 'X2(RL)', 'X2(RR)', 'T(FL)', 'T(FR)', 'T(RL)', 'T(RR)'])
        #plt.plot(parameters, ',-', label=['X2(RL)', 'X2(FL)', 'Z2(RL)', 'Z2(FL)'])
        plt.legend()
        plt.xlabel("t")
        plt.ylabel("parameter")
        plt.grid(True)
        
        # fig, axes = plt.subplots(2)
        # axes[0].plot(parameters)
        # axes[1].plot(parameters)

        plt.show()