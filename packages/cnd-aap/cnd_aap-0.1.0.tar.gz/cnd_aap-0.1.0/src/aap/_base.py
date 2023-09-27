import requests
import cndprint
import urllib3
import json
from .adapter import Adapter
urllib3.disable_warnings()


class Base:
    prefix = "/api/v2/"
    home_path = ''
    
    def __init__(self, adapter, _print):
        self._adapter = adapter
        self._print = _print

    def data(self, name):
        return {"name": name}

    def find_all(self, next_page=None):
        self._print.log_d(f"find_all {type(self).__name__}")
        url = next_page if next_page is not None else self.home_path
        result = self._adapter._query(url)
        items = result["content"]["results"]
        if result["content"]["next"] is not None:
            items += self.find_all(result["content"]["next"])
        return items

    def destroy(self, id):
        self._print.log_d(f"Find_id {type(self).__name__}")
        result = self._adapter._query(f'{self.home_path}/{id}', method="delete")
        if result["status_code"] == 204:
            return True
        return False

    def find_id(self, name):
        self._print.log_d(f"Find_id {type(self).__name__}: {name}")
        result = self._adapter._query(f'{self.home_path}?search={name}')
        return result["content"]["results"][0]["id"]

    def _create(self, data):
        self._print.log_d(f"Create {type(self).__name__}")
        result = self._adapter._query(f"{self.home_path}", method="post", json_data=data)
        return result["content"]["id"]

    def _update(self, id, data):
        self._print.log_d(f"Update {type(self).__name__}")
        result = self._adapter._query(f"{self.home_path}", method="put", json_data=data)
        return result["content"]["id"]

    def create_or_update(self, data):
        self._print.log_d(f"create_or_update {type(self).__name__}")
        id = self.find_id(data["name"])
        if id is not None:
            return self._update(id, data)
        return self._create(data)
