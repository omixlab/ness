from Bio import SeqIO
from .ngrams import split_ngrams

class FASTAIterator:
    
    def __init__(self, fasta_file):
        self.fasta_file = fasta_file
    
    def __iter__(self):
        reader = open(self.fasta_file)
        for record in SeqIO.parse(reader, 'fasta'):
            yield record
        reader.seek(0)

class FASTANgramIterator:

    def __init__(self, fasta_file, ksize=3, both_strands=False, format='str'):
        self.fasta_file = fasta_file
        self.ksize = ksize
        self.both_strands = False
        self.format = format

    def __iter__(self):
        for s, sequence in enumerate(FASTAIterator(self.fasta_file)):
            sequences = [sequence, sequence.reverse_complement()] if self.both_strands else [sequence]
            for sequence in sequences:
                for ngrams_frame in split_ngrams(sequence.seq, ksize=self.ksize, both_strands=self.both_strands):
                    if self.format == 'list':
                        yield ngrams_frame
                    else:
                        yield ' '.join(ngrams_frame)