# NESS

NESS is an alignment-free tool for sequence search based on word embedding. The tool is still under development and the code present in this repository is a proof of concept distributed under the GPL v3 license. 

## Usage

Currently the NESS CLI interface provides the following commands:

### `ness build_model`

Creates a FastText model from a multi FASTA file. 

```
$ ness build_model \
    --input swissprot.fasta \
    --output swissprot.model
```

### `ness build_database`

Similarly to `makeblastdb`, formats a sequence database with vectors computed using a
model previously built. 

```
$ ness build_database \
    --input swissprot.fasta \
    --model swissprot.model \
    --output swissprot
```

### `ness search`

Similarly to the `blast*` programs, compares a multi  FASTA file with the previously formated database.
```
$ ness search --input sequences.fasta --database swissprot --model swissprot.model --out hits.csv
```
# Cite
Kremer, FS *et al* (2021). *NESS: an word embedding-based tool for alignment-free sequence search*. Available at: https://github.com/omixlab/ness. 
