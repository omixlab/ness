from pandas import DataFrame
from abc import abstractmethod
import pickle

class BaseModel:
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def build_model(self, fasta_file:str) -> None:
        pass
    
    @abstractmethod
    def build_database(self, fasta_file:str) -> None:
        pass
    
    @abstractmethod
    def search(self, fasta_file:str) -> DataFrame:
        pass
    
    @abstractmethod
    def save(self, file_name:str) -> None:
        pass
    
    @abstractmethod
    def load(self, file_name:str) -> object:
        pass