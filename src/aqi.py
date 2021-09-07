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

