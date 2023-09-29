from traffic_light_simulator_demo.traffic_light import TrafficLight
from traffic_light_simulator_demo.helpers import handle_input, run_traffic_light_sequence

def main():

    print(" ")
    print ("Welcome to Traffic Light Simulator V1!\n"
           "Please type 'exit' to exit the simulator\n"
           "Or use ctrl+c to terminate the simulator when it's running\n")

    red_time_input = handle_input("How long does RED light stay lit before transitioning?  ")
    green_time_input = handle_input("How long does GREEN light stay lit before transitioning?  ")
    yellow_time_input = handle_input("How long does YELLOW light stay lit before transitioning?  ")

    light = TrafficLight(red_time = red_time_input,
                         green_time = green_time_input, 
                         yellow_time = yellow_time_input)
    run_traffic_light_sequence(light)

if __name__ == "__main__":
    main()
