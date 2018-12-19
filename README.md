# Persper Code Analytics Tool

This project implements the DevRank algorithm for quantiying the structural value of code contributions as described in

> J. Ren\*, H. Yin\*, Q. Hu, A. Fox, W. Koszek. Towards Quantifying the Development Value of Code Contributions. In *FSE (NIER)*, 2018. 

This repo contains a central code analyzer written in python, which given a target git repository, invokes language-specific call graph server to construct the call-commit graph (union of all commits' call graphs) while it iterates through the commits of the repository being analzyed. The resulted call-commit graph is stored in the [CallCommitGraph](/persper/analytics/call_commit_graph.py) class, which knows how to compute DevRanks for functions, commits, and developers.

## Get Started

The following procedure is tested on Ubuntu 16.04 LTS.

1. Install Python (>=3.6)

Download and install Python 3.6+: <https://www.python.org/downloads/>.

Also, create a symbolic link from `python3` to `python` since some scripts reply on it.
```
sudo ln -s /usr/bin/python3 /usr/bin/python
```

2. Install python dependencies (we recommend to use pipenv)

```bash
pipenv install
```

3. Update git

In order to uset the `--indent-heuristic` option of `git diff`, we require git version >= 2.11. Use the following commands to upgrade:

```bash
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt-get update
sudo apt-get install git -y
git --version
```

4. Apply a patch to gitpython

(Try to) apply a patch to gitpython 2.1.x:

```bash
pipenv shell
cd misc/
./apply_patch.py
exit
```

5. Add project directory to path

Add the following line to your `~/.bashrc` file.

```
export PATH=$PATH:/path/to/dir
```

To update your path for the remainder of the session.
```
source ~/.bashrc
```

6. Install srcML for parsing C/C++ and Java

Please download from [here](https://www.srcml.org/#download) and follow the [instructions](http://131.123.42.38/lmcrs/beta/README).

srcML also needs `libarchive-dev` and `libcurl4-openssl-dev`. Install them with the following commands:

```bash
sudo apt install libarchive-dev
sudo apt install libcurl4-openssl-dev
```

```bash
sudo -H pip3 install jupyter
```

To fit notebooks well in git, install jq and run gitconfig.sh. E.g., on Ubuntu:

```bash
sudo apt install -y jq
./gitconfig.sh
```

6. Check setup correctness

```
cd test
pytest
```

You should see all tests passed.

## Interactive mode with jupyter notebook

1. Install Jupyter

Reference <http://jupyter.org/install.html>.

E.g., on Ubuntu LTS 16.04:

```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install jupyter
```

To automaically remove cell outputs and unnecessary meta information from notebook before committing, install jq (a lightweight and flexible command-line JSON processor) and activate it by running gitconfig.sh. E.g., on Ubuntu:

```
sudo apt install -y jq
./gitconfig.sh
```

2. Install pipenv kernel into jupyter notebook

In the project folder, run

```
pipenv shell
```

This will bring up a terminal in your virtualenv like this:

```
(code-analytics-8iDyuztf) bash-3.2$
```

In that shell, do

```
python -m ipykernel install --user --name=my-virtualenv-name
```

Launch jupyter notebook:

```
jupyter notebook
```

In your notebook, the new kernel should now be an option. Enjoy your interactions with the notebook!


## Analyze Javascript Projects

Note: This section will be updated soon as we refactor the js graph server.

Download the submodule `contribs/js-callgraph`:

```bash
git submodule update --init --recursive
```

Run the following commands:

```bash
npm install --prefix contribs/js-callgraph
pipenv install
pipenv run ./tools/repo_creater/create_repo.py test/js_test_repo/
pipenv run pytest test/test_graphs/test_analyzer_js.py
```


## Trouble Shooting

#### 1. No module named 'persper'

Add this repo to python path so python can find the persper package. Insert the following line into `.bashrc` or `.bash_profile`.

```
export PYTHONPATH="/path/to/repo:$PYTHONPATH"
```

<!--### Batch Mode

Complete the basic setup first.
Note: setup-linux-ubuntu.sh can be used for Ubuntu Server.

Read help info of dev_analysis.py:
```bash
./dev_analysis.py -h
```

To output results of PageRank and DevRank over the call graph:
```bash
./dev_analysis.py -x ./repos/linux-4.10-xml/kernel/ -o linux-kernel.xlsx -a 0 1 0.05 -pd
```

To output results of DevRank over the call-commit graph:
```bash
./dev_analysis.py -s ./repos/linux/ -x ./repos/linux-4.10-xml/ -o linux-cc.xlsx -n 100 200 -a 0 1 0.05 -c
```

A sample long-time run:
```bash
nohup ./dev_analysis.py -s ./repos/linux/ -x ./repos/linux-4.10-xml/ -o linux-4.10-cc.xlsx -n 1000 10000 -a 0 1 0.05 -c > dev.out 2>&1 &
```
-->