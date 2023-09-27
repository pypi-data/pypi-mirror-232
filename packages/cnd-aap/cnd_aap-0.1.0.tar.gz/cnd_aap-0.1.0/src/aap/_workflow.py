from ._base import Base
import time


class Workflow(Base):
    home_path = 'workflow_job_templates'

    def data(self, name, inventory_id, description=None, variables={}):
        description = description if description is not None else ''
        return {"name": name, "description": description, "inventory": inventory_id, "variables": variables}
        
    def _execute(self, name, inventory_id):
        self._print.log_d(f"Execute {type(self).__name__}")
        workflow_job_id = self.find_id(name)
        data = {
          "inventory": inventory_id
        }
        result = self._adapter._query(f"{self.home_path}/{workflow_job_id}/launch/", method="post", json_data=data)
        return result["content"]["workflow_job"]
        
    def _wait(self, workflow_job_id):
        iteration_time = 100
        self._print.log_d(f"Wait {type(self).__name__}")
        finished = None
        while finished is not True and iteration_time > 0:
            iteration_time += -1
            time.sleep(10)
            result = self._adapter._query(f"workflow_jobs/{id}/")
            if result["content"]["finished"] is None:
                continue
            finished = True
        if result["content"]["finished"] is None:
            return None
        return not result["content"]["failed"]

    def execute_and_wait(self, name, inventory_id):
        workflow_job_id = self._execute(name, inventory_id)
        return self._wait(workflow_job_id)
