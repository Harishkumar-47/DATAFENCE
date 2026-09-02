class ThreatEngine:

    def analyze(
        self,
        exposure_score,
        inferences
    ):

        threats = []

        if exposure_score >= 70:

            threats.append({
                "type": "DATA_EXPOSURE",
                "severity": "HIGH",
                "score": exposure_score,
                "explanation": (
                    "A large amount of sensitive personal "
                    "information is exposed."
                )
            })

        for inference in inferences:

            if inference["confidence"] >= 0.80:

                threats.append({
                    "type": "INFERENCE_RISK",
                    "severity": inference["severity"],
                    "score": round(
                        inference["confidence"] * 100
                    ),
                    "explanation":
                        inference["explanation"]
                })

        return threats