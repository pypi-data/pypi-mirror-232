import json
from io import StringIO

def toJson(value: str | StringIO):
    from .read import fromEnv
    pd = fromEnv(value)
    return json.dumps(json.loads(pd.to_json(orient="records")), indent=4)

def toEnv(value: str | StringIO):
    from .read import fromJson
    pd = fromJson(value)
    return pd.to_csv(sep="=", header=False, index=False, columns=["name", "value"])