import sys
from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
from requests_mock import Mocker
import yaml
import src.aap as aap
import tests.vars as vars
import cndprint
import time


cnd_print = cndprint.CndPrint(level="Info", uuid="MambaTest", silent_mode=False)
host = ''
with description('CndApp') as self:
    with before.each:
        unstub()
        self.instance = aap.cnd_aap.CndAap(vars.host, _print=vars._print)
        self.instance = self.instance.workflow

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, aap._workflow.Workflow)).to(equal(True))

    with context("data"):
        with it("shoud support the right field"):
            result = self.instance.data("name", "inventory_id", description="description", variables={"a": "b"})
            expected_result = {
                'name': 'name',
                'description': 'description',
                'inventory': 'inventory_id',
                'variables': {'a': 'b'}
            }
            expect(result).to(equal(expected_result))

    with context("_execute", "_execute"):
        with it("shoud return id of the workflow_job"):
            when(self.instance).find_id(...).thenReturn(123)
            with Mocker(real_http=True) as m:
                json_data = vars.read_yaml_file("tests/data/workflows/execute.json")
                m.post(f'{vars.host}/api/v2/workflow_job_templates/123/launch/', status_code=200, json=json_data)
                result = self.instance._execute("My-Workflow", 99)
                expect(result).to(equal(234))

    with context("_wait", "_wait"):
        with before.each:
            when(time).sleep(...).thenReturn(None)
                
        with it("shoud False on failed"):
            when(self.instance).find_id(...).thenReturn(123)
            json_data_wait = vars.read_yaml_file("tests/data/workflows/wait.json")
            json_data_wait_failed = vars.read_yaml_file("tests/data/workflows/wait-failed.json")
            when(self.instance._adapter)._query(...).thenReturn({"content": json_data_wait}).thenReturn({"content": json_data_wait_failed})
            result = self.instance._wait(99)
            expect(result).to(equal(False))
                
        with it("shoud True on success"):
            when(self.instance).find_id(...).thenReturn(123)
            json_data_wait = vars.read_yaml_file("tests/data/workflows/wait.json")
            json_data_wait_failed = vars.read_yaml_file("tests/data/workflows/wait-success.json")
            when(self.instance._adapter)._query(...).thenReturn({"content": json_data_wait}).thenReturn({"content": json_data_wait_failed})
            result = self.instance._wait(99)
            expect(result).to(equal(True))
                
        with it("shoud None if time is over"):
            when(self.instance).find_id(...).thenReturn(123)
            json_data_wait = vars.read_yaml_file("tests/data/workflows/wait.json")
            json_data_wait_failed = vars.read_yaml_file("tests/data/workflows/wait-success.json")
            when(self.instance._adapter)._query(...).thenReturn({"content": json_data_wait})
            result = self.instance._wait(99)
            expect(result).to(equal(None))

    with context("execute_and_wait", "execute_and_wait"):
        with it("shoud execute and wait and return True if success"):
            when(self.instance)._execute(...).thenReturn(None)
            when(self.instance)._wait(...).thenReturn(True)
            result = self.instance.execute_and_wait("name", "inventory_id")
            expect(result).to(equal(True))
            
        with it("shoud execute and wait and return False if failed"):
            when(self.instance)._execute(...).thenReturn(None)
            when(self.instance)._wait(...).thenReturn(False)
            result = self.instance.execute_and_wait("name", "inventory_id")
            expect(result).to(equal(False))

