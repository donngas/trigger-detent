import os
import configparser
import sys

import pygame
import pydirectinput

pygame.init()
pydirectinput.PAUSE = 0.0

# load config
if getattr(sys, 'frozen', False):
    # Running as a bundled executable (PyInstaller)
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as a normal script
    base_dir = os.path.dirname(os.path.abspath(__file__))

config_file_path = os.path.join(base_dir, 'config.ini')

if not os.path.exists(config_file_path):
    print(f"CRITICAL ERROR: config.ini not found at: {config_file_path}")
    print("Please make sure config.ini is in the same folder as the executable.")
    input("Press Enter to exit...")
    sys.exit(1)

config = configparser.ConfigParser()
try:
    config.read(config_file_path, encoding='utf-8')
except Exception as e:
    print(f"Error reading config file: {e}")
    input("Press Enter to exit...")
    sys.exit(1)


l1 = config.get("keybind", "l1")
r1 = config.get("keybind", "r1")
l2 = config.get("keybind", "l2")
r2 = config.get("keybind", "r2")
key_change_behavior = int(config.get("keybind", "key_change_behavior", fallback="0"))
t1 = float(config.get("threshold", "t1"))
t2 = float(config.get("threshold", "t2"))
ltaxis = int(config.get("axis", "ltaxis"))
rtaxis = int(config.get("axis", "rtaxis"))

# Safely get ct_name, removing surrounding quotes if present
raw_ct_name = config.get("calibration", "ct_name", fallback="none")
ct_name = raw_ct_name.strip('"').strip("'")

# Read block_1st_on_release, default to False if not present
if config.get("threshold", "block_1st_on_release").lower() == "true":
    block_1st_on_release = True
else:
    block_1st_on_release = False

HYSTERESIS_MARGIN = 0.05


def get_zone(value, current_zone, t1, t2, margin, block_on_release):
    """
    Determines the current zone based on value and hysteresis.
    Zones: 0 (Neutral), 1 (Zone 1), 2 (Zone 2)
    """
    
    # Define approximate axis floor for release logic
    AXIS_FLOOR = -1.0
    EPSILON = 0.01

    if current_zone == 0:
        if value > t2:
            return 2
        elif value > t1:
            return 1
        else:
            return 0
    elif current_zone == 1:
        if value > t2:
            return 2
        else:
            # Check release condition
            release_threshold = t1 - margin
            
            # If the calculated release threshold is below the physical axis floor,
            # we must release if we are effectively AT the floor.
            if release_threshold < AXIS_FLOOR:
                if value <= AXIS_FLOOR + EPSILON:
                    return 0
                return 1
            else:
                # Normal hysteresis
                if value < release_threshold:
                    return 0
                return 1

    elif current_zone == 2:
        if value < t2 - margin:
            # If blocking 1st detent on release is enabled, 
            # we skip directly to 0 (Neutral).
            if block_on_release:
                return 0

            # Drop down to zone 1 first
            # Logic for 2->?
            # We want to check if we should go to 1 or skip to 0?
            # Standard path is 2->1.
            
            # Check if we also fell below 1->0 threshold
            release_threshold_1 = t1 - margin
            
            # Same floor logic for skipping to 0
            should_go_to_0 = False
            if release_threshold_1 < AXIS_FLOOR:
                if value <= AXIS_FLOOR + EPSILON:
                    should_go_to_0 = True
            elif value < release_threshold_1:
                 should_go_to_0 = True
            
            if should_go_to_0:
                return 0
            else:
                return 1
        else:
            return 2
    return 0


def main():

    clock = pygame.time.Clock()
    done = False

    # pygame will generate a pygame.JOYDEVICEADDED event for every joystick connected at the start of the program
    joysticks = {}
    
    # Track state per controller to handle hysteresis
    # Format: { instance_id: {'lt': zone_int, 'rt': zone_int} }
    controller_states = {}

    # Global set of keys currently currently held down by the program
    current_keys_down = set()

    print("Trigger Detent Started.")
    print(f"Target Controller: {ct_name}")
    print("Press Ctrl+C to quit.")

    warned_multiple_no_filter = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                controller_states[joy.get_instance_id()] = {'lt': 0, 'rt': 0}
                print(f"Joystick connected: {joy.get_name()} (ID: {joy.get_instance_id()})")

            if event.type == pygame.JOYDEVICEREMOVED:
                if event.instance_id in joysticks:
                    del joysticks[event.instance_id]
                    if event.instance_id in controller_states:
                        del controller_states[event.instance_id]
                    print(f"Joystick disconnected (ID: {event.instance_id})")

        # Check for multiple controllers warning condition
        if len(joysticks) > 1 and ct_name.lower() == "none" and not warned_multiple_no_filter:
            print("\nWARNING: Multiple controllers detected but no specific controller filter is set.")
            print("To ensure inputs are read from the correct device, please run Calibrate.exe.")
            warned_multiple_no_filter = True # Warn once per session

        # Calculate which keys should be down this frame
        frame_desired_keys = set()

        new_lt_zone = 0
        new_rt_zone = 0

        for instance_id, joystick in joysticks.items():
            
            # Filter logic
            if ct_name.lower() != "none":
                if joystick.get_name() != ct_name:
                    continue  # Skip checking inputs for this controller

            try:
                left_val = joystick.get_axis(ltaxis)
                right_val = joystick.get_axis(rtaxis)
                
                # Get current state
                state = controller_states.get(instance_id, {'lt': 0, 'rt': 0})
                
                # Calculate new zones with hysteresis
                new_lt_zone = get_zone(left_val, state['lt'], t1, t2, HYSTERESIS_MARGIN, block_1st_on_release)
                new_rt_zone = get_zone(right_val, state['rt'], t1, t2, HYSTERESIS_MARGIN, block_1st_on_release)
                
                # Update state
                controller_states[instance_id] = {'lt': new_lt_zone, 'rt': new_rt_zone}

            except Exception as e:
                # print(f"Error reading joystick: {e}") # Optional debug
                continue

        # --- STEP 1: KEY SELECTION ---
        # Decide WHICH keys should be down based on the zones
        
        if key_change_behavior == 2:
            # Mode 2: Cumulative (Hold 1st while in 2nd)
            if new_lt_zone >= 1:
                frame_desired_keys.add(l1)
            if new_lt_zone == 2:
                frame_desired_keys.add(l2)
            
            # Repeat for Right trigger
            if new_rt_zone >= 1:
                frame_desired_keys.add(r1)
            if new_rt_zone == 2:
                frame_desired_keys.add(r2)

        else:
            # Mode 0 & 1: Exclusive (Only one key at a time)
            if new_lt_zone == 1:
                frame_desired_keys.add(l1)
            elif new_lt_zone == 2:
                frame_desired_keys.add(l2)
            
            if new_rt_zone == 1:
                frame_desired_keys.add(r1)
            elif new_rt_zone == 2:
                frame_desired_keys.add(r2)

        # --- STEP 2: EXECUTION ORDER ---
        # Decide WHEN to press/release the calculated keys

        keys_to_press = frame_desired_keys - current_keys_down
        keys_to_release = current_keys_down - frame_desired_keys

        if key_change_behavior == 1:
            # Mode 1: Clean Handover (Release Old -> Press New)
            # Creates a tiny gap where no keys are pressed.
            for k in keys_to_release:
                pydirectinput.keyUp(k)
            for k in keys_to_press:
                pydirectinput.keyDown(k)

        else:
            # Mode 0 & 2: Standard/Overlap (Press New -> Release Old)
            # Ensures there is always input active (safer for most games).
            # Note: For Mode 2, this order matters less since we rarely release 
            # and press simultaneously, but this is the safe default.
            for k in keys_to_press:
                pydirectinput.keyDown(k)
            for k in keys_to_release:
                pydirectinput.keyUp(k)

        current_keys_down = frame_desired_keys

        clock.tick(30)


if __name__ == "__main__":
    main()