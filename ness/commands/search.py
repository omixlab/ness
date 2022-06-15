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
        df_hits_chunks = database.find_sequences(sequences, k=arguments.hits, threads=arguments.threads, mode=arguments.scann_mode, chunksize=arguments.chunksize)
    else:
        df_hits_chunks = database.find_sequences(sequences, k=arguments.hits, threads=arguments.threads, chunksize=arguments.chunksize)

    for chunk_id, df_hits_chunk in enumerate(df_hits_chunks):
        if chunk_id == 0:
            df_hits_chunk.to_csv(arguments.output, index=False)
        else:
            df_hits_chunk.to_csv(arguments.ouput, index=False, mode='a', header=False)
