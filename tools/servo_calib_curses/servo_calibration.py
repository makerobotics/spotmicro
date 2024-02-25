import curses
from curses.textpad import rectangle
import time
import math
import yaml
ADAFRUIT = 1 # for PC simulation
if ADAFRUIT:
    import Adafruit_PCA9685
import leg

### https://www.marinamele.com/7-tips-to-time-python-scripts-and-control-memory-and-cpu-usage

LEG_LENGTH = 20
LONG_LEG_DISTANCE = 40
LAT_LEG_DISTANCE = 10
DX = 1; DY = 1; DZ = 1
DEBUG = 1

if DEBUG:
    g_file = open("debugdata.log", "a")

g_FL_leg = leg.leg("FL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2)
g_RL_leg = leg.leg("RL", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, LAT_LEG_DISTANCE/2)
g_FR_leg = leg.leg("FR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2)
g_RR_leg = leg.leg("RR", LEG_LENGTH, LEG_LENGTH, 0, 0, 0, -LONG_LEG_DISTANCE/2, -LAT_LEG_DISTANCE/2)

# Sample servo values and target positions
#servo_values = [400] * 12
#target_positions = [350] * 12
g_servo_values = [455, 370, 395, 
                  395, 315, 370, 
                  370, 360, 490, 
                  325, 370, 500] # Initial positions (stand up)
g_servo_values = [205, 645, 410, 
                  130, 590, 365, 
                  620, 100, 485, 
                  590, 100, 510] # Initial positions (sit down)
#g_servo_values = [272, 600, 405, 
#                  173, 573, 365, 
#                  546, 145, 480, 
#                  536, 140, 510] # Initial positions (stand up low)
g_target_positions = g_servo_values.copy()

# Increment target to activate the servos initially (not in target position)
for i in range(0,len(g_target_positions)):
    g_target_positions[i] += 1 
g_selected_channels = []  # List to store selected channels
g_message = "---"
# Functions variables
g_function_text = "Empty"
g_selected_function = 0
g_dir = 1
g_step = 0
g_sequence = 1
g_fps = 0
g_lastTick = time.time()
g_initTime = g_lastTick

if ADAFRUIT:
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)

# Read channel ranges from a YAML file
with open('channel_ranges.yaml', 'r') as file:
    g_channel_data = yaml.safe_load(file)

def debug(text):
    if DEBUG:
        t = time.time()-g_initTime
        g_file.write(f"{t:.3f} - "+text+"\n")

def bound(low, high, value):
    return max(low, min(high, value))

def AngleToPWM(angle, min_pwm, max_pwm, min_angle, max_angle):
    factor = (max_pwm-min_pwm)/(max_angle-min_angle)
    offset = min_pwm - factor*min_angle
    pwm = bound(min(min_pwm, max_pwm), max(min_pwm,max_pwm), int(offset + factor * angle))
    return pwm

def PWMtoAngle(pwm, min_pwm, max_pwm, min_pwm_angle, max_pwm_angle):
    factor = (max_pwm_angle-min_pwm_angle)/(max_pwm-min_pwm)
    offset = min_pwm_angle - factor*min_pwm
    return int(offset + factor*pwm)

def toggle_channel_selection(current_channel):
    if current_channel in g_selected_channels:
        g_selected_channels.remove(current_channel)
    else:
        g_selected_channels.append(current_channel)

def moveChannelTarget(stdscr, current_channel, direction):
    min_pwm_range, max_pwm_range = g_channel_data[current_channel]['range']
    if "R" in direction:
        message = "Move servo right"
        g_target_positions[current_channel] += 5
    else:
        message = "Move servo left"
        g_target_positions[current_channel] -= 5
    # Bound pwm    
    if g_target_positions[current_channel]>max_pwm_range:
        g_target_positions[current_channel] = max_pwm_range
    elif g_target_positions[current_channel]<min_pwm_range:
        g_target_positions[current_channel] = min_pwm_range
    #stdscr.addstr(curses.LINES-2, 0, message)
    #stdscr.refresh()

def edit_channel_target(stdscr, current_channel):
    stdscr.addstr(3 + current_channel, 0, " " * 80)
    stdscr.addstr(3 + current_channel, 0, f"Enter new target position for Channel {current_channel + 1} (Current: {g_target_positions[current_channel]}): ")
    stdscr.refresh()

    stdscr.nodelay(False)
    curses.echo()  # Enable input echoing
    new_target_str = stdscr.getstr().decode('utf-8')
    curses.noecho()  # Disable input echoing
    stdscr.nodelay(True)
    try:
        new_target = int(new_target_str)
        # Limit target position within the specified range
        min_pwm_range, max_pwm_range = g_channel_data[current_channel]['range']
        g_target_positions[current_channel] = max(min(new_target, max_pwm_range), min_pwm_range)
    except ValueError:
        stdscr.addstr(3 + current_channel, 0, "Invalid input. Target position must be an integer.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()  # Wait for user input
        stdscr.nodelay(True)

def edit_target_angle(stdscr, current_channel):
    stdscr.addstr(3 + current_channel, 0, " " * 80)
    stdscr.addstr(3 + current_channel, 0, f"Enter new target angle for Channel {current_channel + 1}: ")
    stdscr.refresh()

    curses.echo()  # Enable input echoing
    stdscr.nodelay(False)
    new_target_str = stdscr.getstr().decode('utf-8')
    stdscr.nodelay(True)
    curses.noecho()  # Disable input echoing

    try:
        new_target = int(new_target_str)
        # Limit target position within the specified range
        min_pwm_range, max_pwm_range = g_channel_data[current_channel]['range']
        min_pwm_angle, max_pwm_angle = g_channel_data[current_channel]['angles']
#        target_positions[current_channel] = max(min(AngleToPWM(new_target, min_range, max_range, min_angle, max_angle), max_range), min_range)
        g_target_positions[current_channel] = AngleToPWM(new_target, min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)
    except ValueError:
        stdscr.addstr(3 + current_channel, 0, "Invalid input. Target angle must be an integer.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()  # Wait for user input
        stdscr.nodelay(True)

def handle_x_key(stdscr, current_channel):
    global g_message, g_selected_channels

    if current_channel in g_selected_channels:
        g_message = "Stopped servo "+str(current_channel)
        if ADAFRUIT:
            pwm.set_pwm(current_channel, 0, 4096)
    else:
        g_message = "Servo is not active."

def display_main_frame(stdscr):
    stdscr.addstr(0, 0, "Servo calibration", curses.A_BOLD)

def display_message(stdscr):
    global g_message

    stdscr.addstr(curses.LINES-2, 0, " "*80)
    stdscr.addstr(curses.LINES-2, 0, g_message)

def display_servo_values(stdscr, current_channel):
    Y_START = 2
    X_START = 0
    LINE_LEN = 62
    stdscr.addstr(Y_START, X_START, "Channel             | PWM | PWM range | Angle | Angle range   ", curses.A_UNDERLINE)
    
    for i, (value, target, channel_info) in enumerate(zip(g_servo_values, g_target_positions, g_channel_data)):
        alias = channel_info.get('alias', f"CH{i + 1}")
        min_pwm_range, max_pwm_range = channel_info['range']
        min_pwm_angle, max_pwm_angle = channel_info['angles']

        if i in g_selected_channels:
            current_angle = PWMtoAngle(value, min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)
            servo_str = f"{alias:20s}| {value:03d}   [{min_pwm_range:03d}, {max_pwm_range:03d}]   {current_angle:03d}°   [{min_pwm_angle:03d}, {max_pwm_angle:03d}]    "
            servo_str += " (Active)"
        else:
            current_angle = PWMtoAngle(target, min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)
            servo_str = f"{alias:20s}| {target:03d}   [{min_pwm_range:03d}, {max_pwm_range:03d}]   {current_angle:03d}°   [{min_pwm_angle:03d}, {max_pwm_angle:03d}]    "
            servo_str += " "*10

        stdscr.addstr(Y_START+1 + i, X_START, servo_str)
        if i in g_selected_channels:
            stdscr.chgat(Y_START+1 + i, X_START, LINE_LEN, curses.A_STANDOUT)
        if i == current_channel:
            stdscr.chgat(Y_START+1 + i, X_START, curses.A_BOLD)
        if i == current_channel and i in g_selected_channels:
            stdscr.chgat(Y_START+1 + i, X_START, LINE_LEN, curses.A_BOLD|curses.A_STANDOUT)

def display_help(stdscr):
    help_text = [
        "Press 'q' to quit.",
        "Use arrow keys to navigate up and down. Inc/dec by left and right.",
        "Press 'a' to edit the target angle of the current channel.",
        "Press 'p' to edit the target raw position of the current channel.",
        "Press 't' to toggle the selection of the current channel.",
        "Press 'x' to stop current servo (pwm = 4096).",
        "Press '0-9' to run program('0' Off, '1' Stand, '2' Sit, '3' Bezier, '4' Walk)."
    ]

    help_win = curses.newwin(len(help_text) + 2, curses.COLS, curses.LINES - len(help_text) - 4, 0)
    help_win.border()

    for i, line in enumerate(help_text):
        help_win.addstr(1 + i, 1, line)

    help_win.refresh()

def closeServos(stdscr):
    for i in range(12):
        stdscr.addstr(curses.LINES-1, 0, "[Status] Close Servo "+str(i))
        stdscr.refresh()
        time.sleep(0.1)
        if ADAFRUIT:
            pwm.set_pwm(i, 0, 4096)
    time.sleep(0.1)

def control_servos(stdscr, current_channel):
    global g_servo_values, g_message

    for i, (value, target, channel_info) in enumerate(zip(g_servo_values, g_target_positions, g_channel_data)):
        min_range, max_range = channel_info['range']
        if i in g_selected_channels:
#            while value != target:
            if value != target:
#                nextvalue = value
                nextvalue = target
#                if target > value:
#                    nextvalue += 1 # todo: improve speed
#                elif target < value:
#                    nextvalue -= 1
#                if nextvalue>max_range or nextvalue<min_range:
#                    break
                if nextvalue>max_range:
                    nextvalue = max_range
                elif nextvalue<min_range:
                    nextvalue = min_range
                value = nextvalue
                if ADAFRUIT:
                    pwm.set_pwm(i, 0, nextvalue)
                g_servo_values[i] = nextvalue
                #g_message = "Move Servo "+str(i)+". val: "+str(value)+" target: "+str(target)+". Ranges: "+str(min_range)+", "+str(max_range)
                #stdscr.addstr(curses.LINES-1, 0, "[Status] "+g_message)
                display_servo_values(stdscr, current_channel)
                stdscr.refresh()

def move_bezier():
    global g_dir, g_step

    g_FL_leg.setPath(g_step/10)
    g_FL_leg.calcInverseKinematics()
    g_FR_leg.setPath(g_step/10)
    g_FR_leg.calcInverseKinematics()
    g_RL_leg.setPath(g_step/10)
    g_RL_leg.calcInverseKinematics()
    g_RR_leg.setPath(g_step/10)
    g_RR_leg.calcInverseKinematics()
    
    g_step += g_dir
    if g_step == 10 or g_step == 0:
        g_dir = -g_dir
        g_FL_leg.reversePath()
        g_FR_leg.reversePath()
        g_RL_leg.reversePath()
        g_RR_leg.reversePath()

def walk(x, y, z, fwd, up):
    global g_sequence, g_message

    # Initial stand up
    if g_sequence == 0:
        g_FL_leg.move_next(x, y, z)
        #g_FR_leg.move_next(x, y, z)
        #g_RL_leg.move_next(x, y, z)
        #g_RR_leg.move_next(x, y, z)
        if(g_FL_leg.Y2 == y):
            g_sequence +=1
    elif g_sequence == 1:
        g_FL_leg.move_next(x, y-up, z)
        #g_FR_leg.move_next(x, y, z)
        #g_RL_leg.move_next(x, y, z)
        #g_RR_leg.move_next(x, y, z)
        if(g_FL_leg.Y2 == y-up):
            g_sequence +=1
    elif g_sequence == 2:
        g_FL_leg.move_next(x+fwd, y-up, z)
        #g_FR_leg.move_next(x, y-up, z)
        #g_RL_leg.move_next(x, y-up, z)
        #g_RR_leg.move_next(x, y-up, z)
        if(g_FL_leg.X2 == x+fwd):
            g_sequence +=1
    elif g_sequence == 3:
        g_FL_leg.move_next(x+fwd, y, z)
        #g_FR_leg.move_next(x+fwd, y-up, z)
        #g_RL_leg.move_next(x+fwd, y-up, z)
        #g_RR_leg.move_next(x+fwd, y-up, z)
        if(g_FL_leg.Y2 == y):
            g_sequence +=1
    elif g_sequence == 4:
        g_FL_leg.move_next(x, y, z)
        #g_FR_leg.move_next(x+fwd, y, z)
        #g_RL_leg.move_next(x+fwd, y, z)
        #g_RR_leg.move_next(x+fwd, y, z)
        if(g_FL_leg.X2 == x):
            g_sequence = 1
    g_message = g_FL_leg.printData()+" -- Step "+str(g_sequence)

def function_positions(stdscr):
    global g_message, g_target_positions

    if g_selected_function == 1:
        g_FL_leg.setSpeeds(5, 5, 5)
        g_FL_leg.move_next(0, 16, 0)
        g_FR_leg.move_next(0, 16, 0)
        g_RL_leg.move_next(0, 16, 0)
        g_RR_leg.move_next(0, 16, 0)
        g_message = g_FL_leg.printData()
        debug("FL * "+g_FL_leg.printData() + " -- x:"+str(g_FL_leg.X2) + ", y:"+str(g_FL_leg.Y2))
        debug("FR * "+g_FR_leg.printData() + " -- x:"+str(g_FR_leg.X2) + ", y:"+str(g_FR_leg.Y2))
    elif g_selected_function == 2:
        g_FL_leg.setSpeeds(1, 1, 1)
        g_FL_leg.move_next(0, 0, 0)
        g_FR_leg.move_next(0, 0, 0)
        g_RL_leg.move_next(0, 0, 0)
        g_RR_leg.move_next(0, 0, 0)
        g_message = g_FL_leg.printData()
    elif g_selected_function == 3:
        move_bezier()
    elif g_selected_function == 4:
        walk(0, 20, 0, 5, 5)
    else:
        return
    # Get angles from legs and calculate corresponding servo positions
    angles_theta1 = [g_FL_leg.theta1 * 180 / math.pi, g_FR_leg.theta1 * 180 / math.pi,
                     g_RL_leg.theta1 * 180 / math.pi, g_RR_leg.theta1 * 180 / math.pi]
    angles_theta2 = [g_FL_leg.theta2 * 180 / math.pi, g_FR_leg.theta2 * 180 / math.pi,
                     g_RL_leg.theta2 * 180 / math.pi, g_RR_leg.theta2 * 180 / math.pi]
    for i in range(4):
        # Knee
        min_pwm_range, max_pwm_range = g_channel_data[i*3]['range']
        min_pwm_angle, max_pwm_angle = g_channel_data[i*3]['angles']        
        g_target_positions[i*3] = AngleToPWM(int(angles_theta2[i]), 
            min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)
        # Shoulder
        min_pwm_range, max_pwm_range = g_channel_data[i*3+1]['range']
        min_pwm_angle, max_pwm_angle = g_channel_data[i*3+1]['angles']
        g_target_positions[i*3+1] = AngleToPWM(int(math.ceil(angles_theta1[i])), 
            min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)
        # Hip
        min_pwm_range, max_pwm_range = g_channel_data[i*3+2]['range']
        min_pwm_angle, max_pwm_angle = g_channel_data[i*3+2]['angles']
        g_target_positions[i*3+2] = AngleToPWM(0, min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)    
        
def calcFPS(stdscr):
    global g_fps, g_lastTick

    t = time.time()
    g_fps = t-g_lastTick
    text = f"FPS: {g_fps:.3f} ms"

    stdscr.addstr(curses.LINES-12, 0, " "*80)
    stdscr.addstr(curses.LINES-12, 0, text)
    g_lastTick = time.time()

def main(stdscr):
    global g_selected_function, g_message
    global g_FL_leg, g_RL_leg, g_FR_leg, g_RR_leg

    current_channel = 0
    curses.curs_set(0)  # Hide cursor

    stdscr.nodelay(True)
    #stdscr.clear()
    stdscr.erase()
    while True:
        function_positions(stdscr)
        control_servos(stdscr, current_channel)
        display_main_frame(stdscr)
        display_servo_values(stdscr, current_channel)
        display_help(stdscr)
        display_message(stdscr)
        calcFPS(stdscr)
        try:
            key = stdscr.getch()
        except:
            key = None
        if key == ord('q'):
            break
        elif key == curses.KEY_UP and current_channel > 0:
            current_channel -= 1
        elif key == curses.KEY_DOWN and current_channel < len(g_servo_values) - 1:
            current_channel += 1
        elif key == curses.KEY_RIGHT:
            moveChannelTarget(stdscr, current_channel, "R")
        elif key == curses.KEY_LEFT:
            moveChannelTarget(stdscr, current_channel, "L")
        elif key == ord('a'):
            # Allow editing the value of the current channel
            edit_target_angle(stdscr, current_channel)
        elif key == ord('p'):
            # Allow editing the target position of the current channel
            edit_channel_target(stdscr, current_channel)
        elif key == ord('t'):
            # Toggle the selection of the current channel
            toggle_channel_selection(current_channel)
        elif key == ord('T'):
            # Toggle all the channels
            for i in range(12):
                toggle_channel_selection(i)
        elif key == ord('x'):
            # Call the function with selected channels and their target positions
            handle_x_key(stdscr, current_channel)
        elif key == ord('0'):
            g_selected_function = 0
            g_message = "Functions off"
        elif key == ord('1'):
            g_selected_function = 1
            g_message = "Stand up active"
        elif key == ord('2'):
            g_selected_function = 2
            g_message = "Sit down active"
        elif key == ord('3'):
            g_selected_function = 3
            g_message = "Bezier active"
            g_FL_leg.sx = g_FL_leg.X2
            g_FL_leg.sy = g_FL_leg.Y2
            g_RL_leg.sx = g_RL_leg.X2
            g_RL_leg.sy = g_RL_leg.Y2
            g_FR_leg.sx = g_FR_leg.X2
            g_FR_leg.sy = g_FR_leg.Y2
            g_RR_leg.sx = g_RR_leg.X2
            g_RR_leg.sy = g_RR_leg.Y2
            
            g_FL_leg.ex = g_FL_leg.X2-5
            g_FL_leg.ey = g_FL_leg.Y2
            g_RL_leg.ex = g_RL_leg.X2-5
            g_RL_leg.ey = g_RL_leg.Y2
            g_FR_leg.ex = g_FR_leg.X2-5
            g_FR_leg.ey = g_FR_leg.Y2
            g_RR_leg.ex = g_RR_leg.X2-5
            g_RR_leg.ey = g_RR_leg.Y2
        elif key == ord('4'):
            g_selected_function = 4
            g_message = "Walk active"
        # Master delay to control speed
        time.sleep(0.01)
        #time.sleep(1.01)
        stdscr.refresh()
    closeServos(stdscr)
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)
