from __future__ import annotations
from ..models import BaseModel
from abc import abstractmethod
import numpy as np
import pandas as pd

class BaseDatabase:
    @abstractmethod
    def __init__(database_path:str, model:BaseModel) -> None:
        pass
    @abstractmethod
    def insert(vectors:np.array, ids=np.array) -> None:
        pass
    @abstractmethod
    def insert_sequences(sequences) -> None:
        pass
    @abstractmethod
    def find(query:np.array, k:int=10) -> pd.DataFrame:
        pass
    @abstractmethod
    def find_sequences(query:np.array, k:int=10) -> pd.DataFrame:
        pass
    @abstractmethod
    def save(path:str=None) -> None:
        pass
    @classmethod
    @abstractmethod
    def load(path) -> BaseDatabase:
        pass