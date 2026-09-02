class RiskEngine:

    def calculate_risk(
        self,
        exposure_score,
        inference_score,
        threat_score,
        blast_radius
    ):
        risk = (
            exposure_score * 0.30
            + inference_score * 0.25
            + threat_score * 0.25
            + blast_radius * 0.20
        )

        return round(min(risk, 100))

    def security_score(self, risk_score):
        return max(0, 100 - risk_score)

    def risk_level(self, risk_score):

        if risk_score >= 80:
            return "CRITICAL"

        if risk_score >= 60:
            return "HIGH"

        if risk_score >= 40:
            return "MODERATE"

        return "LOW"