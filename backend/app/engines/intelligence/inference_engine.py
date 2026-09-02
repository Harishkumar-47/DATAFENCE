class InferenceEngine:

    RULES = [

        {
            "requires": {"location", "activity"},
            "inference": "Behavioral patterns",
            "severity": 65
        },

        {
            "requires": {"location", "purchases"},
            "inference": "Lifestyle patterns",
            "severity": 70
        },

        {
            "requires": {"contacts", "communication"},
            "inference": "Social graph",
            "severity": 75
        },

        {
            "requires": {"search", "activity"},
            "inference": "Interest profile",
            "severity": 60
        },

        {
            "requires": {"location", "activity", "purchases"},
            "inference": "Detailed behavioral profile",
            "severity": 90
        }
    ]

    def analyze(self, data):

        categories = set()

        for item in data.get(
            "data_points",
            []
        ):

            categories.add(
                item.get("type", "").lower()
            )

        findings = []

        for rule in self.RULES:

            if rule["requires"].issubset(categories):

                findings.append({
                    "inference": rule["inference"],
                    "severity": rule["severity"],
                    "source_categories":
                        list(rule["requires"])
                })

        if findings:

            score = max(
                finding["severity"]
                for finding in findings
            )

        else:

            score = 0

        return {
            "score": min(score, 100),
            "findings": findings
        }