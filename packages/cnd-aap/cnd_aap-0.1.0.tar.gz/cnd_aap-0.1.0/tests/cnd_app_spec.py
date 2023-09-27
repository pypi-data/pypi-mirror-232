import sys
from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
import yaml
import src.aap as aap
import tests.vars as vars


with description('CndApp') as self:
    with before.each:
        unstub()
        self.instance = aap.cnd_aap.CndAap(vars.host)

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, aap.CndAap)).to(equal(True))
