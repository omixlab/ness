from .base_database import BaseDatabase
from .faiss_database import FaissDatabase
from .nmlib_database import NmlibDatabase
from .scann_database import ScannDatabase

__all__ = [
    'BaseDatabase',
    'FaissDatabase',
    'NmlibDatabase',
    'ScannDatabase'
]

databases = {
    'faiss': FaissDatabase,
    'nmlib': NmlibDatabase,
    'scann': ScannDatabase,
}

from .utils import load_database