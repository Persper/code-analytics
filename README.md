
## Quick Start

1. Install Jupyter

Reference <http://jupyter.org/install.html>.

E.g., Ubuntu:
```
sudo apt install -y python3 python3-pip
sudo -H pip3 install --upgrade pip
sudo -H pip3 install jupyter
```

Note: Python 3.5+ is required.

2. Install Python packages

```
sudo -H pip3 install networkx numpy gitpython
```

3. Generate XML representations of repos

Download and install srcML: <http://www.srcml.org/>.

Download target repos into `~/Persper/repos` (the assumed default path).
E.g.:
```
git clone https://github.com/torvalds/linux.git ~/Persper/repos/linux
```

Run graphs/srcml. E.g.:
```
./graphs/srcml.py ~/Persper/repos/linux ~/Persper/repos/linux-xml/
```

4. Run a notebook

All notebooks should be run in the root dir of this project.

E.g., the portal notebook for development value analysis:
```
jupyter notebook dev_analysis.ipynb
```

Enjoy your interactions with the notebook!

