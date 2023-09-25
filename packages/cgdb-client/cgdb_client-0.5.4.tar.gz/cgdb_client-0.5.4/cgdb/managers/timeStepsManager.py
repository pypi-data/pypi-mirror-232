from cgdb.resources.timeStep import TimeStep
from cgdb.utils.ManagerMix import ManagerMix


class TimeStepsManager(ManagerMix):
    def __init__(self, client):
        super().__init__(client)

    def time_steps(self):
        content = self.get("time-steps")
        time_steps = []

        for raw in content:
            time_steps.append(TimeStep(**raw))

        return time_steps

    def time_step_by_id(self, id):
        content = self.get("time-steps/id:" + str(id))

        return self.__made_time_step(content)

    def time_step_by_code(self, code: str):
        content = self.get("time-steps/" + str(code))

        return self.__made_time_step(content)

    def __made_time_step(self, properties):
        code = properties["code"]
        id = properties["id"]

        time_step_unit = properties["timeStepInterval"]["stepUnit"]
        time_step_value = properties["timeStepInterval"]["stepValue"]

        if 'timeStepOffset' in properties:
            offset_step_unit = properties["timeStepInterval"]["stepUnit"]
            offset_step_value = properties["timeStepInterval"]["stepValue"]
            return TimeStep(id, code, time_step_unit, time_step_value, offset_step_unit, offset_step_value)

        return TimeStep(id, code, time_step_unit, time_step_value)

