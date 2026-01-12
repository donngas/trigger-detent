import os
import configparser
import sys

import pygame
import pydirectinput

pygame.init()

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
t1 = float(config.get("threshold", "t1"))
t2 = float(config.get("threshold", "t2"))
ltaxis = int(config.get("axis", "ltaxis"))
rtaxis = int(config.get("axis", "rtaxis"))
# Safely get ct_name, removing surrounding quotes if present
raw_ct_name = config.get("calibration", "ct_name", fallback="none")
ct_name = raw_ct_name.strip('"').strip("'")


def main():

    clock = pygame.time.Clock()
    done = False

    # pygame will generate a pygame.JOYDEVICEADDED event for every joystick connected at the start of the program
    joysticks = {}
    
    print("Trigger Detent Started.")
    print(f"Target Controller: {ct_name}")
    print("Press Ctrl+C to quit.")

    warned_multiple_no_filter = False

    while not done:
        for event in pygame.event.get():

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick connected: {joy.get_name()} (ID: {joy.get_instance_id()})")

            if event.type == pygame.JOYDEVICEREMOVED:
                if event.instance_id in joysticks:
                    del joysticks[event.instance_id]
                    print(f"Joystick disconnected (ID: {event.instance_id})")

        # Check for multiple controllers warning condition
        if len(joysticks) > 1 and ct_name.lower() == "none" and not warned_multiple_no_filter:
            print("\nWARNING: Multiple controllers detected but no specific controller filter is set.")
            print("To ensure inputs are read from the correct device, please run Calibrate.exe.")
            warned_multiple_no_filter = True # Warn once per session

        for joystick in joysticks.values():
            
            # Filter logic
            if ct_name.lower() != "none":
                if joystick.get_name() != ct_name:
                    continue  # Skip checking inputs for this controller

            try:
                left_trigger = joystick.get_axis(ltaxis)
                right_trigger = joystick.get_axis(rtaxis)

                if left_trigger > t1 and left_trigger < t2:
                    pydirectinput.press(l1)
                if right_trigger > t1 and right_trigger < t2:
                    pydirectinput.press(r1)
                if left_trigger > t2:
                    pydirectinput.press(l2)
                if right_trigger > t2:
                    pydirectinput.press(r2)

            except:
                continue

        clock.tick(30)


if __name__ == "__main__":
    main()