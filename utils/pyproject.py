"""usage: python pyproject.py project.name"""
import sys
import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
res = data
for key in sys.argv[1].split("."):
    res = res.get(key, {})
print(res)
