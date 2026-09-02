class ThreatEngine:

    def analyze(
        self,
        exposure,
        inference
    ):

        exposure_score = exposure.get(
            "score",
            0
        )

        inference_score = inference.get(
            "score",
            0
        )

        threat_score = (
            exposure_score * 0.45
            +
            inference_score * 0.55
        )

        threat_score = round(
            min(threat_score, 100)
        )

        if threat_score >= 80:
            level = "CRITICAL"

        elif threat_score >= 60:
            level = "HIGH"

        elif threat_score >= 40:
            level = "MODERATE"

        else:
            level = "LOW"

        return {
            "score": threat_score,
            "level": level
        }
