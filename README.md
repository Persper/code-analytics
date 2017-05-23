
## Quick Start

### Interactive Mode

1. Install Python and packages

Download and install Python: <https://www.python.org/downloads/>
Note: Python 3.5+ is required.

Install packages dicttoxml gitpython lxml networkx numpy openpyxl statistics scipy: <https://packaging.python.org/installing/>

E.g., Ubuntu:
```
sudo apt install -y python3 python3-pip
sudo -H pip3 install dicttoxml gitpython lxml networkx numpy openpyxl statistics scipy
```

In order to uset the `--indent-heuristic` option of `git diff`, we require git version >= 2.11. Use the following commands to upgrade:
```
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt-get update
sudo apt-get install git -y
git --version
```

(Try to) apply a patch to gitpython 2.1.x:
```
cd misc/
./apply_patch.py
```

2. Generate XML representations of repos

Download and install srcML: <http://www.srcml.org/>.

Download target repos into `./repos` (the assumed default path).
E.g.:
```
git clone https://github.com/torvalds/linux.git ./repos/linux
git -C ./repos/linux checkout v4.10
```

Run graphs/srcml. E.g.:
```
./graphs/srcml.py ./repos/linux ./repos/linux-4.10-xml/
```

3. Install Jupyter

Reference <http://jupyter.org/install.html>.

E.g., Ubuntu:
```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install jupyter
```

4. Run a notebook

All notebooks should be run in the root dir of this project.

E.g., the portal notebook for development value analysis:
```
jupyter notebook dev_analysis.ipynb
```

Enjoy your interactions with the notebook!

### Batch Mode

Do the above Step 1 and Step 2.
Note: setup-linux-ubuntu.sh can be used for Ubuntu Server.

Read help info of dev_analysis.py:
```
./dev_analysis.py -h
```

To output results of PageRank and DevRank over the call graph:
```
./dev_analysis.py -x ./repos/linux-4.10-xml/kernel/ -o linux-kernel.xlsx -a 0 1 0.05 -pd
```

To output results of DevRank over the call-commit graph:
```
./dev_analysis.py -s ./repos/linux/ -x ./repos/linux-4.10-xml/ -o linux-cc.xlsx -n 100 200 -a 0 1 0.05 -c
```

A sample long-time run:
```
nohup ./dev_analysis.py -s ./repos/linux/ -x ./repos/linux-4.10-xml/ -o linux-4.10-cc.xlsx -n 1000 10000 -a 0 1 0.05 -c > dev.out 2>&1 &
```
