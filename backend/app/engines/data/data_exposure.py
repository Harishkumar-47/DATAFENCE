class DataExposureEngine:

    def calculate(self, discovered_data):

        score = 0

        weights = {
            "HIGH": 25,
            "MEDIUM": 12,
            "LOW": 5
        }

        for item in discovered_data:
            score += weights.get(
                item["sensitivity"],
                0
            )

        return min(score, 100)