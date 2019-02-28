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