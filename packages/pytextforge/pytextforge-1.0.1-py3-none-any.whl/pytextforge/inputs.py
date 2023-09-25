import json
import re

DATA_RE = re.compile(pattern=r'^([a-zA-Z0-9]+)[=](.*)$')

def load_data(string: str) -> tuple[str, str, str]:
    if not DATA_RE.match(string=string):
        return None, None, f"The string '{string}' doesn't fit with the regex '{DATA_RE.pattern}'"
    groups = DATA_RE.match(string=string)
    return groups.group(1), groups.group(2), None

def load_json(string: str) -> tuple[str, dict, str]:
    id, data, err = load_data(string=string)
    if err:
        return None, None, err
    if not data:
        return id, None, None
    try:
        return id, json.loads(s=data), None
    except json.JSONDecodeError as ex:
        return None, None, f"Cannot decode the data '{data}' from the id '{id}', error: {ex}"
    
def process_data(data: list) -> dict:
    tmp = {}
    for d in data:
        if d['data']:
            tmp[d['id']] = d['data']
    return tmp