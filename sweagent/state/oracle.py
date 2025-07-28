from sweagent.types import StepOutput

class Oracle:

    @classmethod
    def verify_step(cls, step_output: StepOutput, step: int) -> bool:
        return True
        # if step > 1:
        #     return False
        # else:
        #     return True
