import pygame
import pydirectinput

pygame.init()


TRANSLATION = {
    "left_trigger_1st": "num1",
    "right_trigger_1st": "num2",
    "left_trigger_2nd": "num4",
    "right_trigger_2nd": "num5",
}


def output_translation(keybind):
    pydirectinput.press(TRANSLATION[keybind])


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

            jid = joystick.get_instance_id()
            left_trigger = joystick.get_axis(4)
            right_trigger = joystick.get_axis(5)

            if left_trigger > -1.0 and left_trigger < 0.5:
                output_translation("left_trigger_1st")
            if right_trigger > -1.0 and right_trigger < 0.5:
                output_translation("right_trigger_1st")
            if left_trigger > 0.5:
                output_translation("left_trigger_2nd")
            if right_trigger > 0.5:
                output_translation("right_trigger_2nd")

        clock.tick(30)


if __name__ == "__main__":
    main()