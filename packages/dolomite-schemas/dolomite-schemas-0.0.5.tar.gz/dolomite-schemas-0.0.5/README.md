<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/dolomite-schemas.svg?branch=main)](https://cirrus-ci.com/github/<USER>/dolomite-schemas)
[![ReadTheDocs](https://readthedocs.org/projects/dolomite-schemas/badge/?version=latest)](https://dolomite-schemas.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/dolomite-schemas/main.svg)](https://coveralls.io/r/<USER>/dolomite-schemas)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/dolomite-schemas.svg)](https://anaconda.org/conda-forge/dolomite-schemas)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/dolomite-schemas)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/dolomite-schemas.svg)](https://pypi.org/project/dolomite-schemas/)
[![Monthly Downloads](https://pepy.tech/badge/dolomite-schemas/month)](https://pepy.tech/project/dolomite-schemas)

# Bioconductor object schemas for Python

## Overview

This package vendors the [Bioconductor object schemas](https://github.com/ArtifactDB/BiocObjectSchemas) for the **dolomite-** Python packages.
The idea is to ensure that downstream packages have consistent access to schemas without the need for a remote look-up.
We put this in a separate package so that schema updates are kept separate from actual programming changes.

## Installation

Developers can install the package through `pip`.

```sh
pip install dolomite-schemas
```

## Usage

Schemas are vendored into the `schemas/` subdirectory in the installation directory.
This directory can be easily found by working back from the **dolomite-schemas** module location:

```python
import dolomite_schemas
os.path.join(os.path.dirname(dolomite_schemas.__file__), "schemas")
```

Application-specific schema-vendoring modules should use the same relative location for their schema subdirectory in the installation directory.

## Developer notes

The schemas are not actually committed to this repository, but are instead obtained by running:

```shell
cd extern && ./fetch.sh
```

This can be modified to point to any relevant version of the schemas.
