echo "NESS  (1 thread)"
echo ''
time python3 ness.py search --input tests/data/query.fasta --model  tests/data/uniprot_sprot.model --database tests/data/uniprot_sprot --output tests/data/uniprot_sprot.csv --threads 1

echo "NESS  (4 threads)"
echo ''
time python3 ness.py search --input tests/data/query.fasta --model  tests/data/uniprot_sprot.model --database tests/data/uniprot_sprot --output tests/data/uniprot_sprot.csv

echo "BLAST (1 thread)"
echo ''
time blastp -query tests/data/query.fasta -db tests/data/uniprot_sprot -out tests/data/teste.txt > /dev/null

echo "BLAST (4 threads)"
echo ''
time blastp -query tests/data/query.fasta -db tests/data/uniprot_sprot -out tests/data/teste.txt -num_threads 4 > /dev/null
