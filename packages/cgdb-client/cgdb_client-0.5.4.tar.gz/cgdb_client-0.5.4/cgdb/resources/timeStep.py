class TimeStep:
    def __init__(self, id: int, code: str, time_step_unit: str, time_step_value: int, time_offset_unit: int = None, time_offset_step: int = None):
        self.time_step_unit = time_step_unit
        self.time_step_value = time_step_value
        self.time_offset_unit = time_offset_unit
        self.time_offset_step = time_offset_step
        self.id = id
        self.code = code

    @property
    def url(self):
        if self.code is not None:
            return "time-steps/" + self.code
        else:
            return "time-steps/id:" + str(self.id)
