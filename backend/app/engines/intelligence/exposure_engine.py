class ExposureEngine:

    SENSITIVE_TYPES = {
        "email": 10,
        "phone": 15,
        "location": 20,
        "contacts": 20,
        "documents": 25,
        "financial": 30,
        "identity": 25,
        "biometric": 30
    }

    def analyze(self, data):

        data_points = data.get("data_points", [])

        if not data_points:
            return {
                "score": 0,
                "exposed_categories": [],
                "total_items": 0
            }

        score = 0
        categories = []

        for item in data_points:

            category = item.get(
                "type",
                "unknown"
            ).lower()

            weight = self.SENSITIVE_TYPES.get(
                category,
                5
            )

            score += weight

            if category not in categories:
                categories.append(category)

        score = min(score, 100)

        return {
            "score": score,
            "exposed_categories": categories,
            "total_items": len(data_points)
        }