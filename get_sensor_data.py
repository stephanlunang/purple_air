import requests
import geocoder
import math
import sys
from pprint import pprint
import RPi.GPIO as GPIO
import time




class LEDs:
    def __init__(self):
        self.state = [0, 0, 0]
        self.green_gpio = 2
        self.yellow_gpio = 3
        self.red_gpio = 4
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.green_gpio, GPIO.OUT)
        GPIO.setup(self.yellow_gpio, GPIO.OUT)
        GPIO.setup(self.red_gpio, GPIO.OUT)

    def green_only(self):
        GPIO.output(self.green_gpio, GPIO.HIGH)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.LOW)

    def yellow_only(self):
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.HIGH)
        GPIO.output(self.red_gpio, GPIO.LOW)
    
    def red_only(self):
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.HIGH)

    def yellow_green(self):
        GPIO.output(self.green_gpio, GPIO.HIGH)
        GPIO.output(self.yellow_gpio, GPIO.HIGH)
        GPIO.output(self.red_gpio, GPIO.LOW)

    def red_yellow():
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.HIGH)

    def all_off():
        GPIO.output(self.green_gpio, GPIO.HIGH)
        GPIO.output(self.yellow_gpio, GPIO.HIGH)
        GPIO.output(self.red_gpio, GPIO.HIGH)
        time.sleep(.3)
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.LOW)



class AQI:
    def __init__(self):
        self.aqi_data = {
            "Good": {
                "breakpoint": [0, 15.4],
                "index": [0, 50],
                "color": "green"
            },
            "Moderate": {
                "breakpoint": [15.5, 35.4],
                "index": [51, 100],
                "color": "yellow"
            },
            "Unhealthy for Sensitive Groups": {
                "breakpoint": [35.5, 65.4],
                "index": [101, 150],
                "color": "orange"
            },
            "Unhealthy": {
                "breakpoint": [65.5, 150.4],
                "index": [151, 200],
                "color": "red"
            },
            "Very Unhealthy": {
                "breakpoint": [150.5, 250.4],
                "index": [201, 300],
                "color": "purple"
            },
            "Hazardous": {
                "breakpoint": [250.5, 1000],
                "index": [301, 1000],
                "color": "maroon"
            }
        }

    def convert_ug_m3_to_index(self, ug_m3):
        for category_name, category in self.aqi_data.items():
            if category["breakpoint"][0] <= ug_m3 <= category["breakpoint"][1]:
                breakpoint_delta = category["breakpoint"][1] - category["breakpoint"][0]
                index_delta = category["index"][1] - category["index"][0]
                adjusted_index = ug_m3 * (index_delta/breakpoint_delta) + category["index"][0]
                return adjusted_index, category_name


class Measurements:
    def __init__(self):
        self._lat_deg_to_miles = 69
        self._long_deg_to_miles = 54.6

    def _lat_diff_to_miles(self, lat_deg_to_miles):
        return lat_deg_to_miles * self._lat_deg_to_miles

    def _long_diff_to_miles(self, long_deg_to_miles):
        return long_deg_to_miles * self._long_deg_to_miles

    @staticmethod
    def _determine_delta_in_long_lat(coord_1, coord_2):
        """
        Determine the delta (in degrees, between the two coordinates)
        Args:
            coord_1: (tuple) (longitude, lattitude)
            coord_2: (tuple) (longitude, lattitude)

        Returns:
            (tuple) (delta_longitude, delta_lattitude)
        """
        _long_delta = abs(coord_1[0] - coord_2[0])
        _lat_delta = abs(coord_1[1] - coord_2[1])
        return _long_delta, _lat_delta

    def determine_distance_from_coordinates_in_miles(self, coord_1, coord_2):
        """
        Determine the delta (in miles, between the two coordinates)
        Args:
            coord_1: (tuple) (longitude, lattitude)
            coord_2: (tuple) (longitude, lattitude)

        Returns:
            (tuple) (delta_longitude_in_miles, delta_lattitude_in_miles)

        """
        _long_delta, _lat_delta = self._determine_delta_in_long_lat(
            coord_1=coord_1, coord_2=coord_2
        )
        _long_delta_in_miles = self._long_diff_to_miles(long_deg_to_miles=_long_delta)
        _lat_delta_in_miles = self._lat_diff_to_miles(lat_deg_to_miles=_lat_delta)
        distance_in_miles = math.sqrt(_long_delta_in_miles ** 2 + _lat_delta_in_miles ** 2)
        return distance_in_miles


class PurpleAPI(LEDs):
    def __init__(self):
        super().__init__()
        self.read_key = "F82687ED-F19E-11EA-8401-42010A800051"
        self.write_key = "F83C22F9-F19E-11EA-8401-42010A800051"
        self.base_url = "https://api.purpleair.com/v1"
        self.parameters = ["latitude", "longitude", "confidence", "pm2.5_10minute",
                           "location_type"]
        self._status_code = None
        self.all_measurements = None
        self.current_location = None
        self.bounding_box_size = .05
        self.closest_sensor = None

    def _all_sensors(self):
        self._get_current_location()
        _http_header = {
            "X-API-Key": self.read_key
        }
        parameters = {
            "fields": ",".join(self.parameters),
            "nwlng": self.current_location[1] - self.bounding_box_size,
            "nwlat": self.current_location[0] + self.bounding_box_size,
            "selng": self.current_location[1] + self.bounding_box_size,
            "selat": self.current_location[0] - self.bounding_box_size
        }
        self._get_current_location()

        _api = "{}/sensors".format(self.base_url)
        response = requests.get(_api, headers=_http_header, params=parameters)
        self._status_code = response.status_code
        if self._status_code != 200:
            print("Status Code: {}".format(self._status_code))
            sys.exit()
        raw_measurements = response.json()["data"]
        returned_fields = response.json()["fields"]
        self.all_measurements = []
        for measurement in raw_measurements:
            entry = {}
            for i, parameter in enumerate(returned_fields):
                entry[parameter] = measurement[i]
            self.all_measurements.append(entry)
        # print("Considering: {} measurements...".format(len(self.all_measurements)))

    def _determine_distance_to_sensors(self):
        self._all_sensors()
        self._get_current_location()
        _non_filtered_measurements = self.all_measurements
        self.all_measurements = []
        for measurement in _non_filtered_measurements:
            if measurement["latitude"]:
                measurement["dist_in_miles"] = \
                    Measurements().determine_distance_from_coordinates_in_miles(
                        coord_1=(measurement["latitude"], measurement["longitude"]),
                        coord_2=(self.current_location[0], self.current_location[1])
                    )
                measurement["index"], measurement["category"] = AQI().convert_ug_m3_to_index(
                    measurement["pm2.5_10minute"]
                )
                self.all_measurements.append(measurement)

    def _filter_only_outdoor_sensors(self):
        _non_filtered_measurements = self.all_measurements
        self.all_measurements = []
        for measurement in _non_filtered_measurements:
            if measurement["location_type"] == 0:
                self.all_measurements.append(measurement)

    def _get_current_location(self):
        # self.current_location = geocoder.ip('me').latlng
        self.current_location = (37.859298, -122.253023)
        # self.current_location = (38.522511, -122.495639)

    def get_local_sensors(self, distance=100.0) -> list:
        self._determine_distance_to_sensors()
        self._filter_only_outdoor_sensors()

        matching_sensors = []
        for measurement in self.all_measurements:
            if measurement["dist_in_miles"] < distance:
                matching_sensors.append(measurement)

        # print("Your Location: {}".format(self.current_location))
        return matching_sensors

    def get_closest_sensor(self):
        no_results = True
        while no_results:
            for distance in range(1,10):
                print("\nSearching for sensors within: {} miles...".format(distance/10))
                matching_sensors = self.get_local_sensors(distance=distance/10)
                if matching_sensors:
                    self.closest_sensor = sorted(matching_sensors, key=lambda k: k['dist_in_miles'])[0]
                    return self.closest_sensor
                else:
                    print("No sensors within: {} miles. Expanding radius.\n".format(distance/10))

    def led_dependent_on_air_quality(self):
         _closest_category = self.closest_sensor["category"]
         if _closest_category.lower() == "good":
             self.green_only()
         elif _closest_category.lower() == "moderate":
             self.yellow_green()
         elif "sensitive" in _closest_category.lower():
             self.yellow_only()
         elif _closest_category.lower() == "uhealthy":
             self.red_yellow()
         else:
             self.red()


if __name__ == "__main__":
    run_forever = True
    while run_forever:
        try:
            purple = PurpleAPI()
            closest_sensor = purple.get_closest_sensor()
            print("\n\nRating: {}\n\n".format(closest_sensor["category"]))
            pprint(closest_sensor)
            purple.led_dependent_on_air_quality()
            time.sleep(120)
        except KeyboardInterrupt:
            purple.all_off()
            run_forever = False
        finally:
            purple.all_off()
            run_forever = False
