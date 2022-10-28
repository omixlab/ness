from argparse import Namespace

def build_model(arguments:Namespace):

    from ness.models import models

    assert (arguments.model_type in models)

    model = models[arguments.model_type](
        vector_size=arguments.vector_size, 
        window_size=arguments.window_size, 
        min_count=arguments.min_count, 
        ksize=arguments.ksize,
        temp_corpus_file=arguments.corpus_file,
        both_strands=arguments.both_strands
    )
    model.build_model(
        fasta_file=arguments.input, 
        epochs=arguments.epochs,
        threads=arguments.threads
    )
    model.save(arguments.output)


