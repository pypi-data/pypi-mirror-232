# Token Efficient Fine Tuning (TEFT)
A library reducing the output size of large language models (LLM)

## Build

Put pypi credentials in `~/.pypirc`. The relevant section should look like this
```
[distutils]
  index-servers =
    testpypi

[pypi]
  username = __token__
  password = pypi-...

[testpypi]
  username = __token__
  password = pypi-...
```

```
python -m build
```

Upload to test index:
```
twine upload --repository testpypi dist/*
```

Upload to prod index:
```
twine upload dist/*
```
