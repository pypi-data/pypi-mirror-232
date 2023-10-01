# taopypy

```
pyproject.tomlのversion更新
(.venv) rm -rf taopypy.egg-info && rm -rf dist
(.venv) python3 -m build && python3 -m twine upload --repository pypi dist/*
```