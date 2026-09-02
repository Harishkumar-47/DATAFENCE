class DataNormalizer:

    def normalize(self, data):
        """
        Convert incoming user data into a common
        DATAFENCE intelligence format.
        """

        if not isinstance(data, dict):
            return {
                "identity": {},
                "data_points": [],
                "connections": [],
                "activities": []
            }

        return {
            "identity": data.get("identity", {}),
            "data_points": data.get("data_points", []),
            "connections": data.get("connections", []),
            "activities": data.get("activities", [])
        }