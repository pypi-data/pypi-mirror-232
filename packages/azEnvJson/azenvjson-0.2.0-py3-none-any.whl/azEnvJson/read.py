import pandas as pd
import json
from io import StringIO

def fromJson(value: str | StringIO):
    data = StringIO(value) if type(value) == str else value
    return pd.read_json(data)

def fromEnv(value: str | StringIO):
    n = ""
    data = StringIO(value) if type(value) == str else value
    for row in data:
        n = f'{n}{row.replace("=","|",1)}'
    return pd.read_csv(StringIO(n), sep="|", names=["name",  "value"])