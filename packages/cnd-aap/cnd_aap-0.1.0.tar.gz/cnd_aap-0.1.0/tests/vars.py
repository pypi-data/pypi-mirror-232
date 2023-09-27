import cndprint
import yaml
import src.aap as aap


creds = {"username": '', "password": ''}
host = 'https://iamnotexisting.com'
_print = cndprint.CndPrint(level="info", uuid=">> ", silent_mode=True)

def read_file(filename):
    return open(filename).read()
    
def read_yaml_file(filename):
    content = read_file(filename)
    return yaml.safe_load(content)
    
adapter = aap.adapter.Adapter(host, creds=creds, _print=_print)
