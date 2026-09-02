class RemediationEngine:

    def apply(self, action):

        if action["mode"] == "USER_APPROVAL":

            return {
                "action_id": action["id"],
                "status": "AWAITING_APPROVAL",
                "message":
                    "User approval is required before applying "
                    "this protection."
            }

        return {
            "action_id": action["id"],
            "status": "APPLIED",
            "message":
                f"Protection applied: {action['action']}"
        }