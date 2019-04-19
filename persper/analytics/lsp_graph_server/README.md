# lsp_graph_server

To try out the graph server backed by LSP, especially the [ccls](https://github.com/MaskRay/ccls)-based one, you need
* Compile [MaskRay/ccls](https://github.com/MaskRay/ccls), the customized ccls fork for graph server.

* Place the compiled binary under `/bin` folder of the repository root, i.e. `/bin/ccls` or `/bin/ccls.exe`.

## Work with notebook

* In the repository root, run `pipenv run ./tools/repo_creater/create_repo.py test/cpp_test_repo/` to create a cpp test repo.

* `jupyter notebook`, then open `notebooks/lsp-ccls.ipynb`

* Execute all the cells

## Work with unit tests

* Open a shell under `/test/test_analytics`, run

    ```powershell
    # run all of the tests
    pipenv run pytest test_analyzer_lsp_ccls.py
    # or run a single test
    pipenv run pytest test_analyzer_lsp_ccls.py::testFeatureBranch
    ```

  * The test results are compared against baseline (by commit) in `/test/test_analytics/baseline`.

  * If there are assertion errors during testing, you can see the actual run result in `/test/test_analytics/actualdump`.

## Current status

### C++ (ccls)

* C++ (ccls) LSP server is written, but its overall analysis speed is slow on large repositories. E.g. on TensorFlow:
```
2019-03-31 01:56:12,998 INFO     [__main__] Checkpoint at 8300, 1429.66s, 14.3s/commit; total 649431.64s, 78.2s/commit.
```
* It's not stable on certain test cases (e.g. `cpp_test_repo`), sometimes regression may happen.

 ```
    E           AssertionError: Extra node: std::RowReader &std::operator>>(std::RowReader &reader, int &rhs).
 ```

* It relies on ANTLR-generated lexer to recognize the identifier token, on which to perform go to definition operations. This lexer is not so reliable when there is macro present in the file. If certain part of the file is not covered by ANTLR token, we won't perform go to defintion there.
* You may see `jsonrpc.exceptions.JsonRpcInvalidRequest: not indexed` , this is due to ccls's job count reporting fluctuation. We have already wait for job count to become zero after sending 'didOpen' request.
* Perhaps we should keep all the files open when analyzing for the call graph.