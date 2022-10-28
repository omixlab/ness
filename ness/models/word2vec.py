from __future__ import annotations
from .base_model import BaseModel
from ness.utils.ngrams import split_ngrams
from ness.utils.fasta import FASTANgramIterator
import numpy as np
import gensim.models
from gensim.models.word2vec import LineSentence
import pickle
import copy
import json
import tempfile
import os

class Word2Vec(BaseModel):

    def __init__(self, vector_size=100, window_size=25, min_count=1, ksize=3, temp_corpus_file=os.path.join(tempfile.TemporaryDirectory().name, 'corpus.txt'), both_strands=False):
        
        self.model = None
        self.config = {'model_type': 'word2vec'}
        self.config['vector_size']  = vector_size
        self.config['window_size']  = window_size
        self.config['min_count']    = min_count
        self.config['ksize']        = ksize
        self.config['both_strands'] = both_strands
        self.temp_corpus_file       = temp_corpus_file

        temp_directory = os.path.dirname(temp_corpus_file)

        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)
    
    
    def build_model(self, fasta_file:str, epochs=3, threads=1) -> None:

        self.model = gensim.models.Word2Vec(
            vector_size=self.config['vector_size'], 
            window=self.config['window_size'], 
            min_count=self.config['min_count'], 
            workers=threads,
            max_vocab_size=20**self.config['ksize'], 
            sg=1
        )
        with open(self.temp_corpus_file, 'w') as corpus_writer:
            for s, sequence_ngrams in enumerate(FASTANgramIterator(fasta_file, ksize=self.config['ksize'], both_strands=self.config['both_strands'])):
                corpus_writer.write(sequence_ngrams)
                corpus_writer.write("\n")

        self.model.build_vocab(corpus_iterable=LineSentence(self.temp_corpus_file), progress_per=1000)
        self.model.train(corpus_iterable=LineSentence(self.temp_corpus_file), epochs=epochs, total_examples=self.model.corpus_count, total_words=self.model.corpus_total_words)       
        
    @staticmethod
    def load(file_name:str) -> Word2Vec:
        
        obj = pickle.load(open(file_name + '.pickle', 'rb'))
        obj.model = gensim.models.Word2Vec.load(file_name + '.vecs')
        obj.config = json.loads(open(file_name + '.json').read())
        return obj