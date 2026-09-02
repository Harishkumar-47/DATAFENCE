class ProfileReconstructor:

    def reconstruct(self, inferences):

        profile = {
            "behavioral_profile": False,
            "lifestyle_profile": False,
            "social_profile": False,
            "confidence": 0
        }

        confidence_values = []

        for inference in inferences:

            if inference["type"] == "INTEREST_PROFILE":
                profile["behavioral_profile"] = True

            if inference["type"] == "LIFESTYLE_PROFILE":
                profile["lifestyle_profile"] = True

            if inference["type"] == "SOCIAL_GRAPH":
                profile["social_profile"] = True

            confidence_values.append(
                inference["confidence"]
            )

        if confidence_values:
            profile["confidence"] = round(
                sum(confidence_values)
                / len(confidence_values),
                2
            )

        return profile