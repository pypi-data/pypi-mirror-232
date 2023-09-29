from distutils.core import setup

setup(
  name = 'traffic_light_simulator_demo',
  packages = ['traffic_light_simulator_demo'],
  version = '0.10',
  license='MIT',
  description = 'traffic light simulator', 
  author = 'Yan', 
  author_email = 'yzhao1990@gmail.com',
  url = 'https://github.com/ydotzh/Traffic_Light_Simulator',
  download_url = 'https://github.com/ydotzh/Traffic_Light_Simulator/archive/refs/tags/v_02.tar.gz',
  keywords = ['Data Challenge'],
  classifiers=[
  ],
  entry_points = {
        'console_scripts': ['traffic-light-simulator-demo=traffic_light_simulator_demo.user_interface:main'],
    },
)
