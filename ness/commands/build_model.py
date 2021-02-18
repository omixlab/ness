from ness.models import FastText

def build_model(arguments):

    model = FastText()
    model.build_model(fasta_file=arguments.input, epochs=1)
    model.save(arguments.output)