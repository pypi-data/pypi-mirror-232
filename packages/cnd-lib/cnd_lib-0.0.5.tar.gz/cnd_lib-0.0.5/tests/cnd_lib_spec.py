from mockito import when, mock, unstub
from expects import *
from mamba import description, context, it
import yaml
import src.cnd_lib as cnd_lib
import tests.vars as vars


with description('Base') as self:
    with before.each:
        unstub()
        self.instance = cnd_lib.cnd_lib.CndLib()

    with context("__init__"):
        with it("shoud get an instance"):
            expect(isinstance(self.instance, cnd_lib.cnd_lib.CndLib)).to(equal(True))