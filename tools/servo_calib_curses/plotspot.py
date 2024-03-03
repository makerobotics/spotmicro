import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

class DynamicThreeDPlotter:
    def __init__(self, points_data, lines_data):
        self.points_data = points_data
        self.lines_data = lines_data

        # Create a 3D axis
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Initialize scatter plot for points
        self.points_scatter = self.ax.scatter([], [], [], c='red', marker='o', label='Points')

        # Initialize line plot for lines
        self.lines_plot, = self.ax.plot([], [], [], c='blue', label='Lines')

    def plot_static_frame(self):
        static_points_data = [(0, 0, 0), (10, 0, 0), (10, 20, 0), (0, 20, 0)]

        # Clear existing points
        self.points_scatter.remove()

        # Plot points
        x, y, z = zip(*static_points_data)
        self.points_scatter = self.ax.scatter(x, y, z, c='red', marker='o', label='Points')

    def plot_points(self, frame):
        # Update points data
        new_points_data = [(x + frame, y, z) for x, y, z in self.points_data]

        # Clear existing points
        #self.points_scatter.remove()

        # Plot points
        x, y, z = zip(*new_points_data)
        self.points_scatter = self.ax.scatter(x, y, z, c='red', marker='o', label='Points')

    def plot_lines(self, frame):
        # Update lines data
        new_points_data = [(x + frame, y, z) for x, y, z in self.points_data]
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
        self.plot_lines(frame)
        self.plot_points(frame)
        
# Sample data for points and lines
points_data = [(5, 5, 5), (15, 5, 5), (15, 25, 5), (5, 25, 5)]
lines_data = [(points_data[i], points_data[i+1]) for i in range(len(points_data)-1)]

# Create an instance of the DynamicThreeDPlotter class
dynamic_plotter = DynamicThreeDPlotter(points_data, lines_data)

# Customize the plot
dynamic_plotter.set_labels('X-axis', 'Y-axis', 'Z-axis')
dynamic_plotter.add_legend()

# Animate the plot
dynamic_plotter.animate(frames=50, interval=200)
