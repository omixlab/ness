setup_environment:
	conda env create -f environment.yml || conda env update -f environment.yml

download_test_data:
	cd tests/data/ \
	&& wget -O uniprot_sprot.fasta.gz \
		ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz \
	&& gzip -d uniprot_sprot.fasta.gz 

test:
	python3 ness.py build_model \
		--input tests/data/uniprot_sprot.fasta \
		--output tests/data/uniprot_sprot.model \
		--debug

	python3 ness.py build_database \
		--input tests/data/uniprot_sprot.fasta \
		--model tests/data/uniprot_sprot.model \
		--output tests/data/uniprot_sprot \
		--records_per_chunk 1000000 \
		--debug

	bash time_benchmark.sh
