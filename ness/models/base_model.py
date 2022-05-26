from __future__ import annotations
from abc import abstractmethod
from ness.utils.ngrams import split_ngrams
from ness.utils.fasta import FASTANgramIterator
import numpy as np
import gensim.models
import pickle
import copy
import json

class BaseModel:

    def __init__(self, vector_size=100, window_size=25, min_count=1, ksize=3, both_strands=False):
        
        self.model = None
        self.config = {'model_type': 'basemodel'}
        self.config['vector_size'] = vector_size
        self.config['window_size'] = window_size
        self.config['min_count']   = min_count
        self.config['ksize']       = ksize

    @abstractmethod    
    def build_model(self, fasta_file:str, epochs=3) -> None:
        return None
        
    def compute_sequence_vector(self, sequence:str) -> None:

        ngrams_frame  = split_ngrams(sequence, ksize=self.config['ksize'])[0]
        ngrams_vector = np.zeros((self.config['vector_size'],))

        for ngram in ngrams_frame:
            try:
                ngrams_vector += self.model.wv[ngram]
            except:
                pass
        if len(ngrams_frame) > 0:
            return ngrams_vector / len(ngrams_frame[0])
        else:
            return ngrams_vector
    
    def save(self, file_name:str) -> None:
        
        self.vector_file_name = file_name + '.vecs'
        self.pickle_file_name = file_name + '.pickle'
        self.config_file_name = file_name + '.json'
        self.model.save(self.vector_file_name)
        obj = copy.copy(self)
        del obj.model

        with open(self.pickle_file_name, 'wb') as pickle_writer:
            pickle_writer.write(pickle.dumps(obj))
        
        with open(self.config_file_name, 'w') as config_writer:
            config_writer.write(json.dumps(obj.config))
    
    @classmethod
    def load(self, file_name:str) -> BaseModel:
            return BaseModel()
        