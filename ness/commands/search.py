from argparse import Namespace
import os
import gzip

def search(arguments:Namespace):

    from ness.databases import load_database
    from Bio import SeqIO

    filename, fileext = os.path.splitext(arguments.input)

    if fileext == '.gz':
        reader = gzip.open(arguments.input, 'rt')
        _, fileext = os.path.splitext(filename)
    else:
        reader = open(arguments.input)
    
    if fileext in ['.fasta', 'fas', 'fa']:
        file_format = 'fasta'
    elif fileext in ['.fastq', '.fq']:
        file_format = 'fastq' 

    database = load_database(arguments.database)

    sequences = SeqIO.parse(reader, file_format)

    if database.database_metadata['database_type'] == 'scann':
        df_hits = database.find_sequences(sequences, k=arguments.hits, threads=arguments.threads, mode=arguments.scann_mode)
    else:
        df_hits = database.find_sequences(sequences, k=arguments.hits, threads=arguments.threads)

    df_hits.to_csv(arguments.output, index=False)