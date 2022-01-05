from __future__ import annotations
from .base_model import BaseModel
from ness.utils.ngrams import split_ngrams
from ness.utils.fasta import FASTANgramIterator
import numpy as np
import gensim.models
import pickle
import copy
import json
import tempfile
import os

class FastText(BaseModel):


    def __init__(self, vector_size=100, window_size=25, min_count=1, ksize=3, temp_corpus_file=os.path.join(tempfile.TemporaryDirectory().name, 'corpus.txt')):
        
        self.model = None
        self.config = {'model_type': 'fasttext'}
        self.config['vector_size'] = vector_size
        self.config['window_size'] = window_size
        self.config['min_count']   = min_count
        self.config['ksize']       = ksize
        self.temp_corpus_file      = temp_corpus_file

        temp_directory = os.path.dirname(temp_corpus_file)

        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)
    
    def build_model(self, fasta_file:str, epochs=3) -> None:

        self.model = gensim.models.FastText(size=self.config['vector_size'], window=self.config['window_size'], min_count=self.config['min_count'], workers=4, sg=1)

        with open(self.temp_corpus_file, 'w') as corpus_writer:
            for sequence_ngrams in FASTANgramIterator(fasta_file, ksize=self.config['ksize']):
                corpus_writer.write(sequence_ngrams)

        self.model.build_vocab(corpus_file=self.temp_corpus_file)
        self.model.train(corpus_file=self.temp_corpus_file, epochs=epochs, total_examples=self.model.corpus_count, total_words=self.model.corpus_total_words)       
    
    @staticmethod
    def load(file_name:str) -> FastText:
        
        obj = pickle.load(open(file_name +'.pickle', 'rb'))
        obj.model = gensim.models.FastText.load(file_name + '.vecs')
        obj.config = json.loads(open(file_name + '.json').read())
        return obj