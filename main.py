import os
import configparser

import pygame
import pydirectinput

pygame.init()

# load config
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')

try:
    config.read(config_file_path)
except Exception as e:
    print(f"Error reading config file: {e}")


l1 = config.get("keybind", "l1")
r1 = config.get("keybind", "r1")
l2 = config.get("keybind", "l2")
r2 = config.get("keybind", "r2")
t1 = float(config.get("threshold", "t1"))
t2 = float(config.get("threshold", "t2"))
ltaxis = int(config.get("axis", "ltaxis"))
rtaxis = int(config.get("axis", "rtaxis"))


def main():

    clock = pygame.time.Clock()
    done = False

    # pygame will generate a pygame.JOYDEVICEADDED event for every joystick connected at the start of the program
    joysticks = {}

    while not done:
        for event in pygame.event.get():

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        for joystick in joysticks.values():

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