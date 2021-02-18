# NESS

NESS is an alignment-free tool for sequence search based on word embedding. The tool is still under development and the code present in this repository is a proof of concept distributed under the GPL v3 license. 

## Setup

NESS can be installed from the Python Package Index (PyPI) using PIP, but it's necessary to have FAISS installed previously.

```
$ conda install -c conda-forge ness
```

## Usage

Currently the NESS CLI interface provides the following commands:

### `ness build_model`

Creates a FastText model from a multi FASTA file. 

```
$ ness build_model \
    --in swissprot.fasta \
    --out swissprot.model
```

### `ness build_database`

Similarly to `makeblastdb`, formats a sequence database with vectors computed using a
model previously built. 

```
$ ness build_database \
    --in swissprot.fasta \
    --model swissprot.model \
    --out swissprot
```

### `ness search`

Similarly to the `blast*` programs, compares a multi  FASTA file with the previously formated database.
```
$ ness search --query sequences.fasta --database swissprot.h5 --out hits.csv
```
# Cite
Kremer, FS *et al* (2021). *NESS: an word embedding-based tool for alignment-free sequence search*. Available at: https://github.com/omixlab/ness. 