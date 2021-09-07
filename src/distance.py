import math


class Distance:
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
