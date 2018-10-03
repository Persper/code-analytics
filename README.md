
## Quick Start

### Run Tests for JavaScript

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

<<<<<<< HEAD
### Setup on Ubuntu
=======
### Use jupyter notebook with pipenv

In the project folder, run

```
pipenv install ipykernel
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

In your notebook, the new kernel should now be an option.

### Trouble Shooting

#### 1. No module named 'persper'

Add this repo to python path so python can find the persper package. Insert the following line into `.bashrc` or `.bash_profile`.

```
export PYTHONPATH="/path/to/repo:$PYTHONPATH"
```

### Interactive Mode
>>>>>>> Get jupyter notebook to work with pipenv

1. Install Python and packages

Download and install Python 3.6+: <https://www.python.org/downloads/>.

Then install packages.

```bash
pipenv install
```

Also, create a symbolic link from `python3` to `python` since some scripts reply on it.
```
sudo ln -s /usr/bin/python3 /usr/bin/python
```

2. Update Git

In order to uset the `--indent-heuristic` option of `git diff`, we require git version >= 2.11. Use the following commands to upgrade:
<<<<<<< HEAD
```
git --version
=======
```bash
>>>>>>> Update README to apply GitPython patch
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt-get update
sudo apt-get install git -y
git --version
```

3. Apply a patch to gitpython

(Try to) apply a patch to gitpython 2.1.x:
```bash
pipenv shell
cd misc/
./apply_patch.py
exit
```

4. Add project directory to path

Add the following line to your `~/.bashrc` file.
```
export PATH=$PATH:/path/to/dir
```

<<<<<<< HEAD
To update your path for the remainder of the session.
```
source ~/.bashrc
```

5. Install srcML for parsing C/C++ and Java

Please download from [here](https://www.srcml.org/#download) and follow the [instructions](http://131.123.42.38/lmcrs/beta/README).

srcML also needs `libarchive-dev` and `libcurl4-openssl-dev`.
```
sudo apt install libarchive-dev
sudo apt install libcurl4-openssl-dev
=======
E.g., on Ubuntu:
```bash
sudo -H pip3 install jupyter
```

To fit notebooks well in git, install jq and run gitconfig.sh. E.g., on Ubuntu:
```bash
sudo apt install -y jq
./gitconfig.sh
<<<<<<< HEAD
>>>>>>> Update README to apply GitPython patch
```

6. Check setup correctness

```
cd test
pytest
```

You should see all tests passed.

### Interactive Mode

1. Install Jupyter

Reference <http://jupyter.org/install.html>.

<<<<<<< HEAD
E.g., on Ubuntu LTS 16.04:
```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install jupyter
=======
```bash
bazel build --config=opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2 //tensorflow/tools/pip_package:build_pip_package
>>>>>>> Update README to apply GitPython patch
```

To fit notebooks well in git, install jq and run gitconfig.sh. E.g., on Ubuntu:
```
sudo apt install -y jq
./gitconfig.sh
```

2. Run a notebook

All notebooks should be run in the root dir of this project.

E.g., the portal notebook for development value analysis:
```bash
jupyter notebook dev_analysis.ipynb
```

Enjoy your interactions with the notebook!

### Batch Mode

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

### Install TensorFlow

Follow this tutorial: https://www.tensorflow.org/install/install_sources.

An example build:

```
bazel build --config=opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2 //tensorflow/tools/pip_package:build_pip_package
```

When running TensorFlow, get out of the tensorflow source dir. Otherwise,
python would prompt an error message "No module named
pywrap_tensorflow_internal".

=======
```
>>>>>>> Get jupyter notebook to work with pipenv
