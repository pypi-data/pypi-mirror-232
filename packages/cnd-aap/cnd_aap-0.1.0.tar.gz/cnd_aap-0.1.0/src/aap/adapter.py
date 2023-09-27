import requests
import cndprint
import urllib3
import json
urllib3.disable_warnings()


class Adapter:
    prefix = "/api/v2/"
    home_path = ''

    def __init__(self, host, creds={"username": None, "password": None}, _print=cndprint.CndPrint()):
        self._host = host
        self._creds = creds
        self._print = _print
        self.default_headers = {"Content-Type": "application/json"}

    def api(self):
        result = self._query('me')
        return result["content"]

    def display_log(self, url, method, response):
        self._print.trace_v(f'Url: {url}')
        self._print.trace_v(f'Method: {method}')
        self._print.trace_v(f'Status Code: {response.status_code}')
        self._print.trace_v(f'Response Content: {response.content}')

    def _query(self, url, method="get", json_data=None, retry=False, retry_count=3):
        if method not in ['get', 'post', 'delete', 'patch', 'put']:
            raise AttributeError("(CND) Method not allowed")
        url = url.replace(self.prefix, '')
        full_url = f"{self._host}{self.prefix}{url}"
        self.kwargs = {}
        if json_data is not None:
            self.kwargs["json"] = json_data
        response = getattr(requests, method)(
            full_url,
            headers=self.default_headers,
            auth=(self._creds["username"], self._creds["password"]),
            verify=False,
            **self.kwargs
        )
        self.display_log(full_url, method, response)
        if response.status_code in [200, 201, 202, 204, 404]:
            return {
                "content": json.loads(response.content),
                "status_code": response.status_code
            }
        self._print.info_e(f'Error with status code: {response.status_code}')
        return False
