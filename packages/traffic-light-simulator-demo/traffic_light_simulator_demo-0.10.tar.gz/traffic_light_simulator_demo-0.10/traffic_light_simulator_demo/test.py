import unittest
from traffic_light_simulator_demo.traffic_light import TrafficLight


class TrafficLightTestCase(unittest.TestCase):

    def test_traffic_light_time_setup(self):
        light = TrafficLight(red_time=3, green_time=2, yellow_time=1)
        self.assertEqual(light.light_time['red'], 3)
        self.assertEqual(light.light_time['green'], 2)
        self.assertEqual(light.light_time['yellow'], 1)

    def test_traffic_light_transition(self):
        traffic_light = TrafficLight(default_color='red')
        self.assertEqual(traffic_light.current_color, 'red')
        traffic_light.switch_to_next_color()
        self.assertEqual(traffic_light.current_color, 'green')
        traffic_light.switch_to_next_color()
        self.assertEqual(traffic_light.current_color, 'yellow')
        traffic_light.switch_to_next_color()
        self.assertEqual(traffic_light.current_color, 'red')

if __name__ == '__main__':
    unittest.main()
