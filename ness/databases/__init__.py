from .base_database import BaseDatabase
#from .faiss_database import FaissDatabase
from .scann_database import ScannDatabase

__all__ = [
    'ScannDatabase'
]

databases = {
    'scann': ScannDatabase,
}

from .utils import load_database