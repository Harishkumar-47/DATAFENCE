class DefenseOrchestrator:

    def create_plan(self, assessment, policy_engine):

        actions = policy_engine.generate(
            assessment
        )

        automatic = [
            action for action in actions
            if action["mode"] == "AUTOMATIC"
        ]

        approval = [
            action for action in actions
            if action["mode"] == "USER_APPROVAL"
        ]

        return {
            "plan_status": "READY",

            "total_actions": len(actions),

            "automatic_actions": len(automatic),

            "approval_required": len(approval),

            "actions": actions
        }