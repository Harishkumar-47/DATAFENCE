class DataDiscoveryEngine:

    def analyze(self, user_data):

        discovered = []

        for item in user_data:

            sensitivity = self.classify_sensitivity(
                item["category"]
            )

            discovered.append({
                "category": item["category"],
                "value": item["value"],
                "sensitivity": sensitivity,
                "source": item["source"]
            })

        return discovered

    def classify_sensitivity(self, category):

        high = {
            "financial",
            "location",
            "identity",
            "health",
            "biometric",
            "contacts"
        }

        medium = {
            "email",
            "phone",
            "purchase",
            "search"
        }

        if category in high:
            return "HIGH"

        if category in medium:
            return "MEDIUM"

        return "LOW"