import sys
from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
from requests_mock import Mocker
import yaml
import requests
import src.aap as aap
import tests.vars as vars


with description('Base') as self:
    
    with before.each:
        unstub()
        self.instance = aap._base.Base(vars.adapter, vars._print)

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, aap._base.Base)).to(equal(True))

#    with context("connect"):
#        with it("shoud return the 'me' information"):
#            with Mocker(real_http=True) as m:
#                result = vars.read_yaml_file("tests/data/base/api.json")
#                m.get(f'{vars.host}/api/v2/me', status_code=200, json=result)
#                result = self.instance.api()
#                expect(result["results"][0]["username"]).to(equal('admin'))
#
#    with context("_query", "_query"):
#        with it("shoud raise an error if method is not correct"):
#            expect(lambda: self.instance._query('', method="wrong_method")).to(raise_error(AttributeError))
#            
#        with it("shoud raise an error if method is not correct"):
#            response = mock({'content': '{}', 'status_code': 500}, spec=requests.Response)
#            when(requests).get(...).thenReturn(response)
#            result = self.instance._query('')
#            expect(result).to(equal(False))

    with context("destroy", "destroy"):
        with it("shoud return True after destroy item"):
            with Mocker(real_http=True) as m:
                m.delete(f'{vars.host}/api/v2//123', status_code=204, json={"content": {}})
                result = self.instance.destroy(123)
                expect(result).to(equal(True))
                    
        with it("shoud return False after destroy item failed"):
            with Mocker(real_http=True) as m:
                m.delete(f'{vars.host}/api/v2//123', status_code=404, json={"content": {}})
                result = self.instance.destroy(123)
                expect(result).to(equal(False))

    with context("_update", "_update"):
        with it("shoud return organization id"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/base/create.json")
                m.put(f'{vars.host}/api/v2/', status_code=201, json=result)
                result = self.instance._update(id, self.instance.data('Abc'))
                expect(result).to(equal(456))

    with context("_create", "_create"):
        with it("shoud return organization id"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/base/create.json")
                m.post(f'{vars.host}/api/v2/', status_code=201, json=result)
                result = self.instance._create(self.instance.data('Abc'))
                expect(result).to(equal(456))

    with context("find_id", "find_id"):
        with it("shoud return organization id"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/base/find.json")
                m.get(f'{vars.host}/api/v2/?search=Org_name', status_code=200, json=result)
                result = self.instance.find_id("Org_name")
                expect(result).to(equal(123))

    with context("find_all", "find_all"):
        with it("shoud return multiple"):
            with Mocker(real_http=True) as m:
                page1 = vars.read_yaml_file("tests/data/base/find_all-page1.json")
                page2 = vars.read_yaml_file("tests/data/base/find_all-page2.json")
                m.get(f'{vars.host}/api/v2/', status_code=200, json=page1)
                m.get(f'{vars.host}/api/v2/?page=2', status_code=200, json=page2)
                result = self.instance.find_all()
                expect(len(result)).to(equal(3))

    with context("create_or_update", "create_or_update"):
        with it("shoud create if find return none"):
            when(self.instance).find_id(...).thenReturn(None)
            when(self.instance)._create(...).thenReturn(1)
            result = self.instance.create_or_update({"name": "Org_name"})
            expect(result).to(equal(1))
            
        with it("shoud update if find return an id"):
            when(self.instance).find_id(...).thenReturn(1)
            when(self.instance)._update(...).thenReturn(2)
            result = self.instance.create_or_update({"name": "Org_name"})
            expect(result).to(equal(2))
