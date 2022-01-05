from __future__ import annotations
from ness.databases import BaseDatabase
from ness.models import BaseModel
from ness.models import load_model
from ness.utils.iteration import iter_chunks
import multiprocessing as mp
import pandas as pd
import numpy as np
import faiss
import json
import copy
import pickle
import os

class FaissDatabase(BaseDatabase):
    
    def __init__(self, database_path:str, model:BaseModel) -> None:
        self.database_path = database_path
        self.config_file_name = os.path.join(database_path, 'database.json')
        self.pickle_file_name = os.path.join(database_path, 'database.pickle')
        self.model_file_name  = os.path.join(database_path, 'model')
        self.model = model
        self.database_metadata = {'records': 0, 'chunks': [], 'database_type': 'faiss'}
        self.last_chunk_id = -1

        if not os.path.isdir(self.database_path):
            os.mkdir(self.database_path)

    def insert_sequences(self, sequences, chunksize=100000) -> None:

        for chunk_id, sequence_chunk in enumerate(iter_chunks(sequences, size=chunksize), start=self.last_chunk_id+1):
            
            sequence_ids, sequence_vectors, sequence_raw = [], [], []

            for r, record in enumerate(sequence_chunk):
                ngrams_frame = self.model.compute_sequence_vector(str(record.seq))
                sequence_vectors.append(ngrams_frame)
                sequence_ids.append(record.id)
                sequence_raw.append(str(record.seq))
                self.database_metadata['records'] += 1
                
            faiss_index_file, numpy_ids_file = self.__save_database_chunk(
                output_basename=os.path.join(self.database_path, 'data'), 
                chunk_id=chunk_id, 
                sequence_ids=sequence_ids, 
                sequence_vectors=sequence_vectors,
                sequence_raw=sequence_raw,
                database_metadata=self.database_metadata
            )

            self.database_metadata['chunks'].append(
                {
                    'chunk_id': chunk_id, 
                    'faiss_index_file': faiss_index_file, 
                    'numpy_ids_file': numpy_ids_file + '.npy'
                }
            )

            self.last_chunk_id = chunk_id

        return r+1

    def find_sequences(self, sequences:np.array, k:int=10, threads=mp.cpu_count(), chunksize=10) -> pd.DataFrame:

        faiss.omp_set_num_threads(threads)
    
        df_results = pd.DataFrame(columns=['query', 'subject', 'cosine_similarity'])

        for chunk in iter_chunks(sequences, threads):

            query_ids = []
            query_vectors = []

            for record in chunk:
                vector = self.model.compute_sequence_vector(str(record.seq))
                query_ids.append(record.id)
                query_vectors.append(vector)
            
            df_query_results = pd.DataFrame(columns=['query', 'subject', 'cosine_similarity'])
            query_vectors_array = np.array(query_vectors).astype(np.float32)
            faiss.normalize_L2(query_vectors_array)

            for chunk in self.database_metadata['chunks']:
                
                subject_ids = np.load(chunk['numpy_ids_file'])
                index = faiss.read_index(chunk['faiss_index_file'])

                hits_distances, hits_indexes = index.search(query_vectors_array, k)
                hits_indexes_adjusted = hits_indexes.reshape(-1, 1)[:,0]
                hits_distances_adjusted = hits_distances.reshape(-1, 1)[:,0]

                hits_ids = subject_ids[hits_indexes_adjusted]

                for h, hit_id in enumerate(hits_ids):
                    
                    df_query_results = df_query_results.append(
                        {'query': record.id, 'subject': hits_ids[h], 'cosine_similarity': hits_distances_adjusted[h]},
                        ignore_index=True
                    )

        df_query_results = df_query_results.groupby(by=['query', 'subject']).max().sort_values(by=['query', 'subject', 'cosine_similarity'], ascending=False)
        return df_query_results

    def save(self, path:str=None) -> None:

        if path is None:
            config_file_name = self.config_file_name
            pickle_file_name = self.pickle_file_name
            model_file_name  = self.model_file_name
        else:
            config_file_name = os.path.join(path, 'database.json')
            pickle_file_name = os.path.join(path, 'database.pickle')
            model_file_name  = os.path.join(path, 'model')
 
        self.model.save(model_file_name)
        
        obj = copy.copy(self)
        del obj.model

        with open(pickle_file_name, 'wb') as pickle_writer:
            pickle_writer.write(pickle.dumps(obj))
        
        with open(config_file_name, 'w') as config_writer:
            config_writer.write(json.dumps(obj.database_metadata))
    
    @staticmethod
    def load(database_path) -> BaseDatabase:
    
        config_file_name = os.path.join(database_path, 'database.json')
        pickle_file_name = os.path.join(database_path, 'database.pickle')
        model_file_name  = os.path.join(database_path, 'model')

        obj = pickle.load(open(pickle_file_name, 'rb'))
        obj.database_metadata = json.loads(open(config_file_name).read())
        obj.model  = load_model(model_file_name)
        return obj
    
    def __save_database_chunk(self, output_basename, chunk_id, sequence_ids, sequence_vectors, sequence_raw, database_metadata):

        if not os.path.isdir(output_basename):
            os.mkdir(output_basename)

        faiss_index_file = os.path.join(output_basename, f'{chunk_id}.index')
        numpy_ids_file   = os.path.join(output_basename, f'{chunk_id}.ids')

        index, sequence_vectors = self.__create_faiss_index(sequence_vectors)
        faiss.write_index(index, faiss_index_file)      
        np.save(numpy_ids_file,  np.array(sequence_ids))

        return faiss_index_file, numpy_ids_file

    def __create_faiss_index(self, sequence_vectors):

        sequence_vectors = np.array(sequence_vectors).astype(np.float32)
        index = faiss.IndexFlatIP(sequence_vectors.shape[1])
        faiss.normalize_L2(sequence_vectors)
        index.train(sequence_vectors)
        index.add(sequence_vectors)

        return index, sequence_vectors