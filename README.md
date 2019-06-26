# Persper Code Analytics Tool

This project implements the DevRank algorithm for quantiying the structural value of code contributions as described in

> J. Ren\*, H. Yin\*, Q. Hu, A. Fox, W. Koszek. Towards Quantifying the Development Value of Code Contributions. In *FSE (NIER)*, 2018. 

This repo contains a central code analyzer written in python, which given a target git repository, invokes language-specific call graph server to construct the call-commit graph (union of all commits' call graphs) while it iterates through the commits of the repository being analzyed. The resulted call-commit graph is stored in the [CallCommitGraph](/persper/analytics/call_commit_graph.py) class, which knows how to compute DevRanks for functions, commits, and developers.

## Get Started

The following procedure is tested on Ubuntu 16.04 LTS.

1. Install Python (>=3.6)

Download and install Python 3.6+: <https://www.python.org/downloads/>.

Also, create a symbolic link from `python3` to `python` since some scripts reply on it.
```sh
sudo ln -s /usr/bin/python3 /usr/bin/python
```

2. Install python dependencies (we recommend to use pipenv)

```sh
pipenv install
```

3. Update git

In order to uset the `--indent-heuristic` option of `git diff`, we require git version >= 2.11. Use the following commands to upgrade:

```sh
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt-get update
sudo apt-get install git -y
git --version
```

4. Add project directory to path

Add the following line to your `~/.bashrc` file.

```sh
export PYTHONPATH=$PYTHONPATH:/path/to/dir
```

To update your path for the remainder of the session.
```sh
source ~/.bashrc
```

5. Install srcML for parsing C/C++ and Java

Please download from [here](https://www.srcml.org/#download) and follow the [instructions](http://131.123.42.38/lmcrs/beta/README).

srcML also needs `libarchive-dev` and `libcurl4-openssl-dev`. Install them with the following commands:

```sh
sudo apt install libarchive-dev
sudo apt install libcurl4-openssl-dev
```

6. Check setup correctness

As the test process will create Git repositories, set up your global Git user name and email before testing:
```sh
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

Run the test process:
```sh
pipenv run pytest test/test_analytics
```

You should see all tests passed.

## Report Test Coverage

We use [coverage.py](https://coverage.readthedocs.io/) and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) to compute test coverage:

```
# Execution
pytest --cov=persper/ test/test_analytics

# Reporting
coverage html

# then visit htmlcov/index.html in your browser
```

