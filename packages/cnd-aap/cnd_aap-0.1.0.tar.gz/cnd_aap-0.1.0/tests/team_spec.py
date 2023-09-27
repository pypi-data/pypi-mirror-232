from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
import tests.vars as vars
import src.aap as aap


with description('Team') as self:
    with before.each:
        unstub()
        self.instance = aap.cnd_aap.CndAap(vars.host, _print=vars._print)
        self.instance = self.instance.team

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, aap._team.Team)).to(equal(True))

    with context("data"):
        with it("shoud support the right field"):
            result = self.instance.data("name", "organization_id", description="description")
            expected_result = {
                'name': 'name',
                'description': 'description',
                'organization': 'organization_id'
            }
            expect(result).to(equal(expected_result))
