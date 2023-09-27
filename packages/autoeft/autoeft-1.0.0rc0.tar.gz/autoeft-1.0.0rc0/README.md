# AutoEFT

![AutoEFT](template/logo/png/logo_300.png?raw=true "AutoEFT")

Automated operator construction for effective field theories.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
1. [Installation](#installation)
    1. [Requirements](#requirements)
    2. [Installing AutoEFT from PyPI](#installing-autoeft-from-pypi)
    3. [Installing AutoEFT from conda-forge](#installing-autoeft-from-conda-forge)
    4. [Building AutoEFT from Source Code](#building-autoeft-from-source-code)
2. [Usage](#usage)
    1. [Model Files](#model-files)
    2. [Basis Construction](#basis-construction)
    3. [Loading Operators](#loading-operators)
3. [License](#license)
4. [Authors](#authors)
5. [Cite](#cite)

## Installation
AutoEFT is available on the [Python Package Index (PyPI)](https://pypi.org/) and the [conda-forge](https://conda-forge.org/) channel.

### Requirements
- [Python](https://www.python.org/) >= 3.8
- [SageMath](https://www.sagemath.org/) >= 9.3
- [FORM](https://www.nikhef.nl/~form/) >= 4.3

#### Dependencies
- [NumPy](https://numpy.org/) >= 1.18
- [packaging](https://github.com/pypa/packaging) >= 17.1
- [pydantic](https://github.com/pydantic/pydantic) ~= 1.9
- [PyYAML](https://pyyaml.org/) >= 5.2
- [Rich](https://github.com/Textualize/rich) >= 12.3
- [SciPy](https://scipy.org/) >= 1.8
- [SemVer](https://github.com/python-semver/python-semver) >= 3.0

### Installing AutoEFT from PyPI
To install AutoEFT using `pip`, an already installed and running version of SageMath is required (see the [Sage Installation Guide](https://doc.sagemath.org/html/en/installation/index.html) and [Alternative Installation using PyPI](https://github.com/sagemath/sage/blob/develop/README.md#alternative-installation-using-pypi)).

To install *autoeft* and its dependencies, run:[^homebrew]
```shell
sage -pip install autoeft
```

[^homebrew]: On *macOS* using [Homebrew](https://brew.sh/), it may be necessary to precede this statement by `PYTHONEXECUTABLE=</path/to/sage>` with the proper path to the SageMath executable inserted.
In addition, it may be necessary to add the path to SageMath’s executables to the `$PATH` environment variable.

### Installing AutoEFT from conda-forge
To install *autoeft* and its dependencies, run:
- with [conda](https://conda.io/):
```shell
conda install autoeft -c conda-forge
```

- with [mamba](https://github.com/mamba-org/mamba):
```shell
mamba install autoeft
```

### Building AutoEFT from Source Code
To build the distribution packages, run:
```shell
git clone https://gitlab.com/auto_eft/autoeft.git autoeft
cd autoeft
python -m build
```

## Usage
Verify the installation by running:
```shell
autoeft --help
```

### Model Files
The *model file* defines the symmetry groups and field content of a low-energy theory in the [YAML](https://yaml.org/) format.
To produce a sample *model file*, run:
```shell
autoeft sample-model > sm.yml
```
The resulting file has the same content as [`models/sm.yml`](models/sm.yml).

To define a custom *model file*, it is recommended to produce a sample file using the `sample-model` sub-command and modify it according to the desired theory.

### Basis Construction
Operator bases are constructed using the `construct` (alias `c`) sub-command.
To show the help message, run:[^form-env]
```shell
autoeft construct --help
```

To construct an operator basis for a low-energy theory, pass a valid *model file* (e.g., [`models/sm.yml`](models/sm.yml), see also [Model Files](#model-files)) and *mass dimension* to the command.
For example, to construct the dimension 6 SMEFT operator basis, run:
```shell
autoeft construct sm.yml 6
# ...
# Constructing operator basis for SMEFT @ d=6
# ...
```
This will create the output directory `efts/sm-eft/6/` in the current working directory, containing the file `stats.yml` and directory `basis/`.
A different output directory can be passed using the `--output` argument.

The file `stats.yml` summarizes the number of *families*, *types*, *terms*, and *operators* of a constructed basis.

The `basis/` directory contains the model (`model.json`) used to construct the basis and operator files in subdirectories of the form `<N>/<family>/<type>.yml`.

[^form-env]: *autoeft* needs to access `form` during the construction. If the *FORM* executable is not on the system `PATH`, the environment variable `AUTOEFT_PATH` can be set to specify a different path (multiple paths are separated by `:`).

### Loading Operators
Once a basis is constructed, the operator files can be processed further.
If you want to work with the operators inside SageMath, *autoeft* provides functionality to load the basis:
```py
from pathlib import Path

from autoeft.io.basis import BasisFile

basis_path = Path("efts/sm-eft/6/basis")
basis_file = BasisFile(basis_path)
model = basis_file.get_model()
basis = basis_file.get_basis()

print(model)
# SMEFT: Standard Model Effective Field Theory

LQQQ = basis[{"LL": 1, "QL": 3}]
print(LQQQ)
# LL (1) QL(3)

print(LQQQ.n_terms , LQQQ.n_operators , sep=" & ")
# 3 & 57
```

## License
[MIT](LICENSE)

## Authors
- Robert V. Harlander (RWTH Aachen University)
- Magnus C. Schaaf (RWTH Aachen University)

## Cite
If you use AutoEFT in your project, please refer to:
- <!DOCTYPE html> <html> <body> <p><b> <a href="https://inspirehep.net/literature/2658915"> Standard model effective field theory up to mass dimension 12 </a> </b></p>  <p><a href="https://inspirehep.net/authors/1006678">R.V. Harlander</a> (<a href="https://inspirehep.net/institutions/910724">RWTH Aachen U.</a>), <a href="https://inspirehep.net/authors/2658916">T. Kempkens</a> (<a href="https://inspirehep.net/institutions/910724">RWTH Aachen U.</a>), <a href="https://inspirehep.net/authors/2658917">M.C. Schaaf</a> (<a href="https://inspirehep.net/institutions/910724">RWTH Aachen U.</a>)</p>  <p> e-Print: <a href="https://arxiv.org/abs/2305.06832"> 2305.06832 </a>[hep-ph]</p> <p> DOI: <a href="https://doi.org/10.1103/PhysRevD.108.055020"> 10.1103/PhysRevD.108.055020 </a>(publication) </p> <p> Published in:<span> Phys.Rev.D 108 (2023) 5, 055020</span></p> <br> </body> </html>
---
