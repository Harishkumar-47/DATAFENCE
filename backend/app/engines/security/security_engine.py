from app.engines.security.risk_engine import RiskEngine
from app.engines.security.security_policy import SecurityPolicyEngine
from app.engines.security.defense_orchestrator import DefenseOrchestrator
from app.engines.security.remediation_engine import RemediationEngine
from app.engines.security.verification_engine import VerificationEngine


class SecurityEngine:

    def __init__(self):

        self.risk_engine = RiskEngine()

        self.policy_engine = SecurityPolicyEngine()

        self.orchestrator = DefenseOrchestrator()

        self.remediation = RemediationEngine()

        self.verification = VerificationEngine()


    def assess(
        self,
        exposure_score,
        inference_score,
        threat_score,
        blast_radius
    ):

        risk_score = self.risk_engine.calculate_risk(
            exposure_score,
            inference_score,
            threat_score,
            blast_radius
        )

        security_score = self.risk_engine.security_score(
            risk_score
        )

        risk_level = self.risk_engine.risk_level(
            risk_score
        )

        return {
            "risk_score": risk_score,
            "security_score": security_score,
            "risk_level": risk_level,
            "exposure_score": exposure_score,
            "inference_score": inference_score,
            "threat_score": threat_score,
            "blast_radius": blast_radius
        }


    def create_protection_plan(self, assessment):

        return self.orchestrator.create_plan(
            assessment,
            self.policy_engine
        )


    def protect(self, plan):

        results = []

        for action in plan["actions"]:

            result = self.remediation.apply(
                action
            )

            results.append(result)

        verification = self.verification.verify(
            results
        )

        return {
            "protection_status": "PROCESSED",

            "results": results,

            "verification": verification
        }