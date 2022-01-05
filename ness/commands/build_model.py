from argparse import Namespace

def build_model(arguments:Namespace):

    from ness.models import models

    assert (arguments.model_type in models)

    model = models[arguments.model_type](
        vector_size=arguments.vector_size, 
        window_size=arguments.window_size, 
        min_count=arguments.min_count, 
        ksize=arguments.ksize
    )
    model.build_model(
        fasta_file=arguments.input, 
        epochs=arguments.epochs
    )
    model.save(arguments.output)


