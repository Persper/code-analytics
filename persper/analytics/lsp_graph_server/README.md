# lsp_graph_server

To try out the graph server backed by LSP, especially the [ccls](https://github.com/MaskRay/ccls)-based one, you need
* Compile [ccls-prime](https://github.com/Persper/ccls-prime), the customized ccls fork for graph server.
* Place the compiled binary under `bin` folder of the repository root.
* In the repository root, run `pipenv run ./tools/repo_creater/create_repo.py test/cpp_test_repo/` to create a cpp test repo.
* `jupyter notebook`, then open `notebooks/lsp-ccls.ipynb`
* Execute all the cells
