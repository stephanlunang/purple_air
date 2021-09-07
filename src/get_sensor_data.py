import sys
import time
import requests

from pprint import pprint

from src.leds import LEDs
from src.distance import Distance
from src.aqi import AQI


class PurpleAPI:
    def __init__(self):
        self.leds = LEDs()
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
                    Distance().determine_distance_from_coordinates_in_miles(
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
            for distance in range(1, 10):
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
            self.leds.green_only()
        elif _closest_category.lower() == "moderate":
            self.leds.yellow_green()
        elif "sensitive" in _closest_category.lower():
            self.leds.yellow_only()
        elif _closest_category.lower() == "uhealthy":
            self.leds.red_yellow()
        else:
            self.leds.red_only()


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
            purple.leds.all_off()
            run_forever = False
        finally:
            purple.leds.all_off()
            run_forever = False
