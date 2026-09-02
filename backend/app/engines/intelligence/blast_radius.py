class BlastRadiusEngine:

    WEIGHTS = {
        "email": 10,
        "contacts": 15,
        "documents": 20,
        "financial": 30,
        "identity": 20,
        "location": 10,
        "biometric": 30
    }

    def calculate(self, data):

        connections = data.get(
            "connections",
            []
        )

        score = 0

        for connection in connections:

            category = connection.get(
                "type",
                ""
            ).lower()

            score += self.WEIGHTS.get(
                category,
                5
            )

        return {
            "score": min(score, 100),
            "connected_services":
                len(connections)
        }