class SecurityPolicyEngine:

    def generate(self, assessment):

        actions = []

        if assessment["exposure_score"] >= 70:

            actions.append({
                "id": "DF-EXPOSURE-001",
                "category": "DATA_MINIMIZATION",
                "priority": "HIGH",
                "mode": "AUTOMATIC",
                "action": "REDUCE_EXPOSURE",
                "description":
                    "Identify unnecessary data access and recommend "
                    "removal or restriction."
            })

        if assessment["inference_score"] >= 70:

            actions.append({
                "id": "DF-INFERENCE-001",
                "category": "INFERENCE_PROTECTION",
                "priority": "HIGH",
                "mode": "AUTOMATIC",
                "action": "LIMIT_PROFILE_BUILDING",
                "description":
                    "Reduce combinations of data that enable "
                    "high-confidence behavioral inference."
            })

        if assessment["threat_score"] >= 70:

            actions.append({
                "id": "DF-THREAT-001",
                "category": "ACCOUNT_SECURITY",
                "priority": "CRITICAL",
                "mode": "USER_APPROVAL",
                "action": "HARDEN_ACCOUNT",
                "description":
                    "Recommend stronger account protection and "
                    "security controls."
            })

        if assessment["blast_radius"] >= 70:

            actions.append({
                "id": "DF-BLAST-001",
                "category": "ACCESS_CONTROL",
                "priority": "HIGH",
                "mode": "USER_APPROVAL",
                "action": "REVIEW_CONNECTED_SERVICES",
                "description":
                    "Review connected services that could expose "
                    "multiple categories of personal information."
            })

        return actions