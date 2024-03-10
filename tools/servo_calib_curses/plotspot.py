import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

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
                trigger = 70
                trigger_distance = 2*self.FWD_REV/3
                if self.FWD_REV-(2*trigger_distance) <= self.x <= self.FWD_REV-trigger_distance:
                    trigger = 71
                    print(str(self.FWD_REV-(2*trigger_distance))+" < "+str(self.x)+" < "+str(self.FWD_REV-trigger_distance))
                elif self.x <= self.FWD_REV-(2*trigger_distance):
                    trigger = 72
                if self.x <= -self.FWD_REV:
                    self.phase = 0
                    trigger = 73
            case _:
                print("Unexpected phase!")
        print(f"Leg {self.name} in phase {self.phase:d},{trigger:d} at ({self.x:2.1f}, {self.y:2.1f}, {self.z:2.1f})")
        return trigger
    
class Walking:
    def __init__(self, height):
        self.height = height
        self.UP = 5
        self.FWD = 5
        self.leg_FL = Walking_Leg("FL", 0, 0, height)
        self.leg_FR = Walking_Leg("FR", 0, 0, height)
        self.leg_RL = Walking_Leg("RL", 0, 0, height)
        self.leg_RR = Walking_Leg("RR", 0, 0, height)

        self.phase = 0

    def walk(self, speed):
        match self.phase:
            case 0:
                if self.leg_RL.run(speed) == 6: # Transition to phase 3 (touch ground)
                    self.phase += 1
            case 1:
                self.leg_FL.run(speed)
                self.leg_RL.run(speed)
                return
            case _:
                pass

class DynamicThreeDPlotter:
    def __init__(self, legs):
        self.legs = legs
        self.counter = 0
        # Create a 3D axis
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        # Initialize scatter plot for points
        self.points_scatter = self.ax.scatter([], [], [], c='red', marker='o', label='Points')
        # Initialize line plot for lines
        self.lines_plot, = self.ax.plot([], [], [], c='blue', label='Lines')

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
            new_points_data.append((static_points_data[i][0]+self.legs[self.counter][i][0],
                                 static_points_data[i][1]+self.legs[self.counter][i][1],
                                 static_points_data[i][2]+self.legs[self.counter][i][2]))
        #print(new_points_data)
        self.counter += 1
        if self.counter == 30:
            self.counter = 0

        # Clear existing points
        #self.points_scatter.remove()

        # Plot points
        x, y, z = zip(*new_points_data)
        self.points_scatter = self.ax.scatter(x, y, z, c='green', marker='o', label='Points')

    def plot_lines(self, frame):
        # Update lines data
        new_points_data = [(x, y, z) for x, y, z in self.points_data]
        new_lines_data = [(new_points_data[i], new_points_data[i+1]) for i in range(len(new_points_data)-1)]

        # Clear existing lines
        self.lines_plot.remove()

        # Plot lines
        x_lines, y_lines, z_lines = zip(*sum(new_lines_data, ()))
        self.lines_plot, = self.ax.plot(x_lines, y_lines, z_lines, c='blue', label='Lines')

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
        #self.plot_lines(frame)
        self.plot_points(frame)
        

# Run this if standalone (test purpose)
if __name__ == '__main__':
    legs = []
    w = Walking(-20)
    for i in range(60):
        w.walk(0.2)
        legs.append([(w.leg_FR.x, w.leg_FR.y, w.leg_FR.z),
                     (w.leg_FL.x, w.leg_FL.y, w.leg_FL.z),
                     (w.leg_RR.x, w.leg_RR.y, w.leg_RR.z),
                     (w.leg_RL.x, w.leg_RL.y, w.leg_RL.z)])
    
    # Create an instance of the DynamicThreeDPlotter class
    dynamic_plotter = DynamicThreeDPlotter(legs)

    # Customize the plot
    dynamic_plotter.set_labels('X-axis', 'Y-axis', 'Z-axis')
    dynamic_plotter.add_legend()

    # Animate the plot
    dynamic_plotter.animate(frames=30, interval=200)
