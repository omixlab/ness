from argparse import Namespace

def search(arguments:Namespace):

    from ness.databases import load_database
    from Bio import SeqIO

    database = load_database(arguments.database)

    sequences = SeqIO.parse(open(arguments.input), 'fasta')

    df_hits = database.find_sequences(sequences, k=10, chunksize=10, threads=arguments.threads)
    df_hits.to_csv(arguments.output, index=False)