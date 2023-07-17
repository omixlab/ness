setup:
	conda env create -f environment.yml || conda env update -f environment.yml

download_test_data:
	mkdir -p tests/data/raw
	mkdir -p tests/data/models
	mkdir -p tests/data/databases
	mkdir -p tests/data/results
	
	wget -O tests/data/raw/uniprot_sprot.fasta.gz https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
	gzip -d -f tests/data/raw/uniprot_sprot.fasta.gz
	mv tests/data/raw/uniprot_sprot.fasta tests/data/raw/swissprot.fasta

test:
	pytest tests/

build_pypi_package:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	python setup.py sdist bdist_wheel

twine_upload: build_pypi_package
	@twine upload \
		--repository-url https://upload.pypi.org/legacy/ \
		-u $(PYPI_USER) \
		-p $(PYPI_PASS) \
		dist/*-py3-none-any.whl