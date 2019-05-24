## pytest

Our recommended way to run tests is through [pytest](https://docs.pytest.org/en/latest/).

It should have been installed if you have run `pipenv install`. Otherwise, install pytest with your favorite package manager:

```bash
// pip
$ pip install -U pytest

// or conda
$ conda install pytest
```

## Run Tests

To run the entire test suite, simply:

```
cd ${root}
pipenv run pytest -s test/
```

To test a specific module:

```
pipenv run pytest -s <test_module>.py
```

To learn more about how pytest detects tests, follow this [link](https://docs.pytest.org/en/latest/goodpractices.html#goodpractices).

## Tests that are ignored

You can ignore certain tests by customizing test collection using `conftest.py`. For details, please see [here](https://docs.pytest.org/en/latest/example/pythoncollection.html#customizing-test-collection).

Here is a list of tests that are currently ignored:

1. `test/test_analytics/test_analyzer_cpp.py`
2. `test/test_analytics/test_analyzer_lsp_ccls.py`



