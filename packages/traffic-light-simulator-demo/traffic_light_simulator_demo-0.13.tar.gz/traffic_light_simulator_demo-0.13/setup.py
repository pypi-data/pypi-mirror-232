from distutils.core import setup

setup(
  name = 'traffic_light_simulator_demo',
  packages = ['traffic_light_simulator_demo'],
  include_package_data=True,
  version = '0.13',
  license='MIT',
  description = 'traffic light simulator', 
  author = 'Yan', 
  author_email = 'yzhao1990@gmail.com',
  url = 'https://github.com/ydotzh/Traffic_Light_Simulator',
  download_url = 'https://github.com/ydotzh/Traffic_Light_Simulator/archive/refs/tags/v_013.tar.gz',
  keywords = ['Data Challenge'],
  classifiers=[
  ],
  entry_points = {
        'console_scripts': ['traffic-light-simulator-demo=traffic_light_simulator_demo.user_interface:main'],
    },
)
