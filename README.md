# Build Pip Package
```
python3 -m build 
pip install dist/pydict-0.1.tar.gz 
```

# Install via makepkg (Install deps, make and install)
```
makepkg -sif
```

# Run at dev machine
## Setup virtual environment
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Launch Program
```
cd py_src
python3 -m pydict
```