download_test_data:
	cd tests/data/ \
	&& wget -O uniprot_sprot.fasta.gz \
		ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz \
	&& gzip -d uniprot_sprot.fasta.gz 

setup_environment:
	conda env create -f environment.yml || conda env update -f environment.yml

install:
	python3 setup.py build
	python3 setup.py install

test:
	python3 ness.py build_model \
		--input tests/data/uniprot_sprot.fasta.subset \
		--output tests/data/uniprot_sprot.subset.model \
		--debug
	
	python3 ness.py build_database \
		--input tests/data/uniprot_sprot.fasta.subset \
		--model tests/data/uniprot_sprot.subset.model \
		--output tests/data/uniprot_sprot.subset \
		--debug
	
	python3 ness.py search \
		--input tests/data/uniprot_sprot.fasta.subset \
		--output tests/data/uniprot_sprot.subset.out \
		--model tests/data/uniprot_sprot.subset \
		--database tests/data/uniprot_sprot.subset \
		--debug