from __future__ import annotations
from .base_model import BaseModel
from ness.utils.ngrams import split_ngrams
from ness.utils.fasta import FASTANgramIterator
import numpy as np
import gensim.models
import pickle
import copy

class FastText(BaseModel):

    def __init__(self, vector_size=100, window_size=25, min_count=1, ksize=3):
        
        self.model = None
        self.vector_size = vector_size
        self.window_size = window_size
        self.min_count = min_count
        self.ksize = ksize
    
    def build_model(self, fasta_file:str, epochs=3) -> None:

        self.model = gensim.models.FastText(size=self.vector_size, window=self.window_size, min_count=self.min_count, workers=4, sg=1)
        self.model.build_vocab(sentences=FASTANgramIterator(fasta_file, ksize=self.ksize))
        self.model.train(sentences=FASTANgramIterator(fasta_file, ksize=self.ksize), epochs=epochs, total_examples=self.model.corpus_count)

    def compute_sequence_vector(self, sequence:str) -> None:

        ngrams_frames = split_ngrams(sequence, ksize=self.ksize)
        ngrams_frames_vectors = np.zeros((self.ksize, self.vector_size))

        for k, ngrams_frame in enumerate(ngrams_frames):

            for ngram in ngrams_frame:
                try:
                    ngrams_frames_vectors[k,:] += self.model.wv[ngram]
                except:
                    pass    
        return ngrams_frames_vectors
    
    def save(self, file_name:str) -> None:

        self.model.save(file_name + '.vecs')
        obj = copy.copy(self)
        del obj.model
        pickle.dump(obj, open(file_name, 'wb'))
    
    @classmethod
    def load(self, file_name:str) -> FastText:
        
        obj = pickle.load(open(file_name, 'rb'))
        obj.model = gensim.models.FastText.load(file_name + '.vecs')
        return obj