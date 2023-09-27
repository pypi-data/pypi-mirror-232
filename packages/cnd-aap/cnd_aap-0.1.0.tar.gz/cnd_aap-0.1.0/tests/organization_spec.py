from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
from requests_mock import Mocker
import tests.vars as vars
import src.aap as aap


with description('Organization') as self:
    with before.each:
        unstub()
        self.instance = aap.cnd_aap.CndAap(vars.host, _print=vars._print)
        self.instance = self.instance.organization

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, aap._organization.Organization)).to(equal(True))

    with context("data", "data"):
        with it("shoud return data"):
            result = self.instance.data('Abc')
            expect(result).to(equal({"name": "Abc", "description": ''}))

    with context("_update", "_update"):
        with it("shoud return organization id"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/organizations/create.json")
                m.put(f'{vars.host}/api/v2/organizations', status_code=201, json=result)
                result = self.instance._update(id, self.instance.data('Abc'))
                expect(result).to(equal(456))

    with context("_create", "_create"):
        with it("shoud return organization id"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/organizations/create.json")
                m.post(f'{vars.host}/api/v2/organizations', status_code=201, json=result)
                result = self.instance._create(self.instance.data('Abc'))
                expect(result).to(equal(456))

    with context("find_id", "find_id"):
        with it("shoud return organization id"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/organizations/find.json")
                m.get(f'{vars.host}/api/v2/organizations?search=Org_name', status_code=200, json=result)
                result = self.instance.find_id("Org_name")
                expect(result).to(equal(123))

    with context("find_all", "find_all"):
        with it("shoud return multiple"):
            with Mocker(real_http=True) as m:
                page1 = vars.read_yaml_file("tests/data/organizations/find_all-page1.json")
                page2 = vars.read_yaml_file("tests/data/organizations/find_all-page2.json")
                m.get(f'{vars.host}/api/v2/organizations', status_code=200, json=page1)
                m.get(f'{vars.host}/api/v2/organizations?page=2', status_code=200, json=page2)
                result = self.instance.find_all()
                expect(len(result)).to(equal(3))
