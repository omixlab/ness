from argparse import Namespace

def build_database(arguments:Namespace):

    from ness.databases import databases
    from ness.models import load_model
    from ness.utils.fasta import FASTAIterator
    
    model = load_model(arguments.model)    
    fasta_iterator = FASTAIterator(arguments.input)

    assert (arguments.database_type in databases)
    
    database = databases[arguments.database_type](database_path=arguments.output, model=model, slicesize=arguments.slicesize, jumpsize=arguments.jumpsize)
    database.insert_sequences(fasta_iterator, chunksize=arguments.chunksize)
    database.save()