setup:
	conda env create -f environment.yml || conda env update -f environment.yml

download_test_data:
	mkdir -p tests/data/
	cd tests/data/ \
	&& wget -O uniprot_sprot.fasta.gz \
		ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz \
	&& gzip -d uniprot_sprot.fasta.gz 

test:
	#ness build_model \
	#	--input tests/data/uniprot_sprot.fasta \
	#	--output tests/data/uniprot_sprot.model \
	#	--corpus-file tests/data/corpus.txt \
	#	--debug

	ness build_database \
		--input tests/data/uniprot_sprot.fasta \
		--model tests/data/uniprot_sprot.model \
		--output tests/data/uniprot_sprot \
		--chunksize 1000000 \
		--debug

	#bash time_benchmark.sh
