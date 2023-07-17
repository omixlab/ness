from .fasttext import FastText
from .word2vec import Word2Vec
from .esm import ESM1
from .base_model import BaseModel

__all__ = [
    'Word2Vec',
    'FastText',
    'ESM1',
    'BaseModel'
]

models = {
    'word2vec': Word2Vec,
    'fasttext': FastText,
    'esm1': ESM1
}

from .utils import load_model