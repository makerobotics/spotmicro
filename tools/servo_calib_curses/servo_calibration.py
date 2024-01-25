import curses
import time
import yaml
ADAFRUIT = 1 # for PC simulation
if ADAFRUIT:
    import Adafruit_PCA9685

# Sample servo values and target positions
#servo_values = [400] * 12
#target_positions = [350] * 12
servo_values = [455, 370, 395, 395, 315, 370, 370, 360, 490, 325, 370, 500] # Initial positions
target_positions = servo_values.copy()

# Increment target to activate the servos initially (not in target position)
for i in range(0,len(target_positions)):
    target_positions[i] += 1 
selected_channels = []  # List to store selected channels
message = "---"

if ADAFRUIT:
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)

# Read channel ranges from a YAML file
with open('channel_ranges.yaml', 'r') as file:
    channel_data = yaml.safe_load(file)

def AngleToPWM(angle, min_pwm, max_pwm, min_angle, max_angle):
    factor = (max_pwm-min_pwm)/(max_angle-min_angle)
    offset = min_pwm - factor*min_angle 
    return int(offset + factor*angle)

def PWMtoAngle(pwm, min_pwm, max_pwm, min_pwm_angle, max_pwm_angle):
    factor = (max_pwm_angle-min_pwm_angle)/(max_pwm-min_pwm)
    offset = min_pwm_angle - factor*min_pwm
    return int(offset + factor*pwm)
    
def display_servo_values(stdscr, current_channel):
    stdscr.clear()
    stdscr.addstr(0, 0, "Servo calibration", curses.A_BOLD)
    stdscr.addstr(2, 0, "Channel             | PWM | PWM range | Angle | Angle range   ", curses.A_UNDERLINE)
    
    for i, (value, target, channel_info) in enumerate(zip(servo_values, target_positions, channel_data)):
        alias = channel_info.get('alias', f"CH{i + 1}")
        min_pwm_range, max_pwm_range = channel_info['range']
        min_pwm_angle, max_pwm_angle = channel_info['angles']
        current_angle = PWMtoAngle(value, min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)

        #servo_str = f"{alias}: {formatted_value} (Target: {formatted_target}) | Range: [{min_range:02d}, {max_range:02d}]"
        servo_str = f"{alias:20s}| {target:03d}   [{min_pwm_range:03d}, {max_pwm_range:03d}]   {current_angle:03d}°   [{min_pwm_angle:03d}, {max_pwm_angle:03d}]    "

        if i in selected_channels:
            servo_str += " (Active)"

        stdscr.addstr(3 + i, 0, servo_str)
        if i in selected_channels:
            stdscr.chgat(3 + i, 0, curses.A_STANDOUT)
        if i == current_channel:
            stdscr.chgat(3 + i, 0, curses.A_BOLD)
        if i == current_channel and i in selected_channels:
            stdscr.chgat(3 + i, 0, curses.A_BOLD|curses.A_STANDOUT)
            
    stdscr.addstr(curses.LINES-2, 0, message)
    stdscr.refresh()

def display_help(stdscr):
    help_text = [
        "Press 'q' to quit.",
        "Use arrow keys to navigate up and down.",
        "Press 'a' to edit the target angle of the current channel.",
        "Press 'p' to edit the target raw position of the current channel.",
        "Press 't' to toggle the selection of the current channel.",
        "Press 'x' to stop current servo (pwm = 4096)."
    ]

    help_win = curses.newwin(len(help_text) + 2, curses.COLS, curses.LINES - len(help_text) - 4, 0)
    help_win.border()

    for i, line in enumerate(help_text):
        help_win.addstr(1 + i, 1, line)

    help_win.refresh()

def handle_s_key(channels, target_positions):
    # Example function, replace with your own logic
    aliases = [channel_data[channel].get('alias', f"CH{channel + 1}") for channel in channels]
    print(f"Function called with Channels {channels} ({aliases}) and Target Positions {target_positions}")

def handle_x_key(stdscr, current_channel):
    global message

    if current_channel in selected_channels:
        message = "Stopped servo "+str(current_channel)
        if ADAFRUIT:
            pwm.set_pwm(current_channel, 0, 4096)
    else:
        message = "Servo is not active."
    stdscr.addstr(curses.LINES-2, 0, message)
    stdscr.refresh()


def edit_channel_value(stdscr, current_channel):
    stdscr.addstr(3 + current_channel, 0, " " * 80)
    stdscr.addstr(3 + current_channel, 0, f"Enter new value for CH {current_channel + 1} (Target: {target_positions[current_channel]}): ")
    stdscr.refresh()

    curses.echo()  # Enable input echoing
    new_value_str = stdscr.getstr().decode('utf-8')
    curses.noecho()  # Disable input echoing

    try:
        new_value = int(new_value_str)
        # Limit value within the specified range
        min_range, max_range = channel_data[current_channel]['range']
        servo_values[current_channel] = max(min(new_value, max_range), min_range)
    except ValueError:
        stdscr.addstr(3 + current_channel, 0, "Invalid input. Value must be an integer.")
        stdscr.refresh()
        stdscr.getch()  # Wait for user input

def moveChannelTarget(stdscr, current_channel, direction):
    if "R" in direction:
        message = "Move servo right"
        target_positions[current_channel] += 5
    else:
        message = "Move servo left"
        target_positions[current_channel] -= 5
    stdscr.addstr(curses.LINES-2, 0, message)
    stdscr.refresh()

def edit_channel_target(stdscr, current_channel):
    stdscr.addstr(3 + current_channel, 0, " " * 80)
    stdscr.addstr(3 + current_channel, 0, f"Enter new target position for Channel {current_channel + 1} (Current: {target_positions[current_channel]}): ")
    stdscr.refresh()

    curses.echo()  # Enable input echoing
    new_target_str = stdscr.getstr().decode('utf-8')
    curses.noecho()  # Disable input echoing

    try:
        new_target = int(new_target_str)
        # Limit target position within the specified range
        min_pwm_range, max_pwm_range = channel_data[current_channel]['range']
        target_positions[current_channel] = max(min(new_target, max_pwm_range), min_pwm_range)
    except ValueError:
        stdscr.addstr(3 + current_channel, 0, "Invalid input. Target position must be an integer.")
        stdscr.refresh()
        stdscr.getch()  # Wait for user input

def edit_target_angle(stdscr, current_channel):
    stdscr.addstr(3 + current_channel, 0, " " * 80)
    stdscr.addstr(3 + current_channel, 0, f"Enter new target angle for Channel {current_channel + 1}: ")
    stdscr.refresh()

    curses.echo()  # Enable input echoing
    new_target_str = stdscr.getstr().decode('utf-8')
    curses.noecho()  # Disable input echoing

    try:
        new_target = int(new_target_str)
        # Limit target position within the specified range
        min_pwm_range, max_pwm_range = channel_data[current_channel]['range']
        min_pwm_angle, max_pwm_angle = channel_data[current_channel]['angles']
#        target_positions[current_channel] = max(min(AngleToPWM(new_target, min_range, max_range, min_angle, max_angle), max_range), min_range)
        target_positions[current_channel] = AngleToPWM(new_target, min_pwm_range, max_pwm_range, min_pwm_angle, max_pwm_angle)
    except ValueError:
        stdscr.addstr(3 + current_channel, 0, "Invalid input. Target angle must be an integer.")
        stdscr.refresh()
        stdscr.getch()  # Wait for user input

def toggle_channel_selection(current_channel):
    if current_channel in selected_channels:
        selected_channels.remove(current_channel)
    else:
        selected_channels.append(current_channel)

def closeServos(stdscr):
    for i in range(12):
        stdscr.addstr(curses.LINES-1, 0, "[Status] Close Servo "+str(i))
        stdscr.refresh()
        time.sleep(0.1)
        if ADAFRUIT:
            pwm.set_pwm(i, 0, 4096)
    time.sleep(0.5)

def control_servos(stdscr):
    global servo_values, message

    for i, (value, target, channel_info) in enumerate(zip(servo_values, target_positions, channel_data)):
        min_range, max_range = channel_info['range']
        if i in selected_channels:
            while value != target:
                nextvalue = value
                if target > value:
                    nextvalue += 1
                elif target < value:
                    nextvalue -= 1
                if nextvalue>max_range or nextvalue<min_range:
                    break
                value = nextvalue
                if ADAFRUIT:
                    pwm.set_pwm(i, 0, nextvalue)
                servo_values[i] = nextvalue
                time.sleep(0.05)
                message = "Move Servo "+str(i)+". val: "+str(value)+" target: "+str(target)+". Ranges: "+str(min_range)+", "+str(max_range)
                stdscr.addstr(curses.LINES-2, 0, message)
                stdscr.refresh()
                
def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    current_channel = 0

    while True:
        control_servos(stdscr)
        display_servo_values(stdscr, current_channel)
        display_help(stdscr)
        
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_UP and current_channel > 0:
            current_channel -= 1
        elif key == curses.KEY_DOWN and current_channel < len(servo_values) - 1:
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
        #elif key == ord('s'):
        #    # Call the function with selected channels and their target positions
        #    handle_s_key(selected_channels, [target_positions[channel] for channel in selected_channels])
        elif key == ord('x'):
            # Call the function with selected channels and their target positions
            handle_x_key(stdscr, current_channel)
        elif key == ord('t'):
            # Toggle the selection of the current channel
            toggle_channel_selection(current_channel)

    closeServos(stdscr)
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)
