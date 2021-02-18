from Bio import SeqIO
from .ngrams import split_ngrams

class FASTAIterator:
    
    def __init__(self, fasta_file):
        self.fasta_file = fasta_file
    
    def __iter__(self):
        reader = open(self.fasta_file)
        for record in SeqIO.parse(reader, 'fasta'):
            yield str(record.seq)

class FASTANgramIterator:

    def __init__(self, fasta_file, ksize=3):
        self.fasta_file = fasta_file
        self.ksize = ksize

    def __iter__(self):
        for s, sequence in enumerate(FASTAIterator(self.fasta_file)):
            for ngrams_frame in split_ngrams(sequence, ksize=self.ksize):
                yield ngrams_frame