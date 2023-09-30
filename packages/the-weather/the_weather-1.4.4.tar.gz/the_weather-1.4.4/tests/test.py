import unittest
from the_weather import *

class WeatherTest(unittest.TestCase):
    
    def test_init(self):
        weather = Weather(22025)
        self.assertEqual(weather.res.status_code, 200)
    

if __name__ == '__main__':
    unittest.main()