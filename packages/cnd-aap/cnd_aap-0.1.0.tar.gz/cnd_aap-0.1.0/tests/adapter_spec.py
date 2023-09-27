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
        self.instance = aap.adapter.Adapter(vars.host, creds=vars.creds, _print=vars._print)

    with context("__init__"):
        with it("shoud set the host, username and password"):
            expect(self.instance._host).to(equal(vars.host))

    with context("connect"):
        with it("shoud return the 'me' information"):
            with Mocker(real_http=True) as m:
                result = vars.read_yaml_file("tests/data/base/api.json")
                m.get(f'{vars.host}/api/v2/me', status_code=200, json=result)
                result = self.instance.api()
                expect(result["results"][0]["username"]).to(equal('admin'))

    with context("_query", "_query"):
        with it("shoud raise an error if method is not correct"):
            expect(lambda: self.instance._query('', method="wrong_method")).to(raise_error(AttributeError))
            
        with it("shoud raise an error if method is not correct"):
            response = mock({'content': '{}', 'status_code': 500}, spec=requests.Response)
            when(requests).get(...).thenReturn(response)
            result = self.instance._query('')
            expect(result).to(equal(False))
