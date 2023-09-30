import sys
import time

def handle_input(prompt):
    """
    Take and process user prompt, and returns output_time
    Args:
        prompt: user input
    Returns:
        output_time: number of seconds for a traffic light to be lit.
    """
    user_input = input(prompt)
    while True:
        if user_input == 'exit':
            print("Existing Traffic Light Simulator.")
            sys.exit()
        try:
            output_time = int(float(user_input))
            if output_time >  0:
                return output_time
            else:
                print("Invalid input. Please type a positive number.")
                user_input = input(prompt)
        except ValueError:
            print("Invalid input. Please type a positive number.")
            user_input = input(prompt)

def display_and_switch(traffic_light):
    """
    display the current light for a pre defined period of time, and then switch
    to the next color.
    Args:
        traffic_light: TrafficLight object
    """
    light_seconds_current = traffic_light.get_current_time()
    color_current = traffic_light.get_current_color()
    while light_seconds_current > 0:
        print("\n")
        print("%s lgiht is on, with %s seconds remaining" % (color_current, light_seconds_current))
        print(traffic_light.get_current_ascii_art())
        if light_seconds_current >= 1:
            time.sleep(1)
            light_seconds_current -= 1
    traffic_light.switch_to_next_color()


def run_traffic_light_sequence(traffic_light):
    """
    Run the full traffic light sequence. i.e., from red->green->yellow->red
    The light will be switched for three times
    Args:
        traffic_light: TrafficLight object
    """
    light_to_switch = 3
    while light_to_switch > 0:
        display_and_switch(traffic_light)
        light_to_switch -= 1
