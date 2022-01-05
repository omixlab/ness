from .fasttext import FastText
from .word2vec import Word2Vec
from .base_model import BaseModel

__all__ = [
    'Word2Vec',
    'FastText',
    'BaseModel'
]

models = {
    'word2vec': Word2Vec,
    'fasttext': FastText
}

from .utils import load_model