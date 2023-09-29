# Lifecycle state broadcast SDK

Python SDK version for the Lifecycle state broadcast Restful API

## Building package

```bash
python setup.py sdist bdist_wheel
```

## Publishing package

```bash
python -m twine upload dist/*
```

This will ask for credentials:

username: __token__
password: Your PyPi API Token
