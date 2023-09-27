import sys
from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
import yaml
import src.aap as aap
import tests.vars as vars
import cndprint


cnd_print = cndprint.CndPrint(level="Info", uuid="MambaTest", silent_mode=False)
host = ''
with description('CndApp') as self:
    with before.each:
        unstub()
        self.instance = aap.cnd_aap.CndAap(vars.host, _print=vars._print)
        self.instance = self.instance.group

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, aap._group.Group)).to(equal(True))

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
