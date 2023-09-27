import cndprint
from ._inventory import Inventory  # noqa: F401
from ._workflow import Workflow  # noqa: F401
from ._team import Team  # noqa: F401
from ._organization import Organization  # noqa: F401
from ._host import Host  # noqa: F401
from ._group import Group  # noqa: F401
from ._base import Base
from .adapter import Adapter  # noqa: F401
import os


class CndAap(Base):
    def __init__(self, host, creds={"username": None, "password": None}, _print=cndprint.CndPrint()):
        self._adapter = Adapter(host, creds=creds, _print=_print)
        self._get_all_subclass()
        for sub_class_name in CndAap._get_all_subclass():
            sub_class = eval(sub_class_name)
            setattr(self, sub_class.__name__.lower(), sub_class(self._adapter, _print))

    @staticmethod
    def _filename_to_camel_case(filename):
        str = filename.split('.')[0][0:]
        temp = str.split('_')
        res = ''.join(ele.title() for ele in temp[0:])
        return res

    @staticmethod
    def _get_all_subclass():
        files = filter(lambda my_file: (my_file[0] == '_' and my_file[1] != '_' and my_file != '_base.py'), os.listdir("src/aap"))
        my_list = list(files)
        return [CndAap._filename_to_camel_case(my_file) for my_file in my_list]
