import os

PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

class TrafficLight():

    def __init__(self,
                 default_color='red',
                 red_time=1,
                 yellow_time=1,
                 green_time=1):
        """
        Initiazlie the object with light time and ascii art.
        
    Args:
        default_color: the traffic color to be first lit.
        red_time: number of seconds RED light will be turned on.
        green_time: number of seconds GREEN light will be turned on.
        yellow_time: number of seconds YELLOW light will be turned on.
        """
        red_ascii_art = open(PACKAGE_ROOT + '/traffic_light_art/red.txt', 'r').read()
        green_ascii_art = open(PACKAGE_ROOT + '/traffic_light_art/green.txt', 'r').read()
        yellow_ascii_art = open(PACKAGE_ROOT + '/traffic_light_art/yellow.txt', 'r').read()
        self.light_ascii_art = {
            'red': red_ascii_art,
            'green': green_ascii_art,
            'yellow': yellow_ascii_art
        }
        self.light_time = {
            'red': red_time,
            'green': green_time,
            'yellow': yellow_time
        }
        self.current_color = default_color

    def get_current_ascii_art(self):
        """ returns ASCII art for the current color """
        return self.light_ascii_art[self.current_color]

    def get_current_color(self):
        """ returns current color in string """
        return self.current_color

    def get_current_time(self):
        """ returns remaining time for the current color """
        return self.light_time[self.current_color]

    def switch_to_next_color(self):
        """ switch from current color to the next one following the sequence:
            red, green, yellow, red ...
        """
        if self.current_color == 'red':
            self.current_color = 'green'
        elif self.current_color == 'green':
            self.current_color = 'yellow'
        else :
            self.current_color = 'red'
