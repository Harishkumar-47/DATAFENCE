class InferenceEngine:

    def analyze(self, data):

        categories = {
            item["category"]
            for item in data
        }

        inferences = []

        if {
            "search",
            "purchase",
            "location"
        }.issubset(categories):

            inferences.append({
                "type": "INTEREST_PROFILE",
                "confidence": 0.91,
                "severity": "HIGH",
                "evidence": [
                    "Search activity",
                    "Purchase history",
                    "Location patterns"
                ],
                "explanation": (
                    "Combined behavioral signals can reveal "
                    "long-term interests and preferences."
                )
            })

        if {
            "location",
            "purchase"
        }.issubset(categories):

            inferences.append({
                "type": "LIFESTYLE_PROFILE",
                "confidence": 0.84,
                "severity": "HIGH",
                "evidence": [
                    "Location history",
                    "Purchase behavior"
                ],
                "explanation": (
                    "Location and purchasing patterns can "
                    "reveal lifestyle characteristics."
                )
            })

        if {
            "contacts",
            "email"
        }.issubset(categories):

            inferences.append({
                "type": "SOCIAL_GRAPH",
                "confidence": 0.88,
                "severity": "HIGH",
                "evidence": [
                    "Contacts",
                    "Email relationships"
                ],
                "explanation": (
                    "Communication metadata can reveal "
                    "relationships and social connections."
                )
            })

        return inferences