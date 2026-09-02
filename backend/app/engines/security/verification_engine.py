class VerificationEngine:

    def verify(self, results):

        applied = [
            result for result in results
            if result["status"] == "APPLIED"
        ]

        pending = [
            result for result in results
            if result["status"] == "AWAITING_APPROVAL"
        ]

        return {
            "verification_status": "COMPLETE",

            "successful": len(applied),

            "pending": len(pending),

            "success_rate":
                round(
                    (len(applied) / len(results)) * 100,
                    2
                ) if results else 100
        }