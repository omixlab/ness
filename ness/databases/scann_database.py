from __future__ import annotations
from ness.databases import BaseDatabase
from ness.models import BaseModel
from ness.models import load_model
from ness.utils.iteration import iter_chunks, slice_sequences
import multiprocessing as mp
import logging
import pandas as pd
import numpy as np
import h5py
import json
import copy
import pickle
import os

class ScannDatabase(BaseDatabase):
    
    def __init__(self, database_path:str, model:BaseModel, slicesize=None, jumpsize=None) -> None:
        self.database_path = database_path
        self.h5_file_name = os.path.join(database_path, 'database.h5')
        self.config_file_name = os.path.join(database_path, 'database.json')
        self.pickle_file_name = os.path.join(database_path, 'database.pickle')
        self.model_file_name  = os.path.join(database_path, 'model')
        self.model = model
        self.database_metadata = {'records': 0, 'chunks': [], 'database_type': 'scann'}
        self.database_metadata['slicesize'] = slicesize
        self.database_metadata['jumpsize'] = jumpsize
        self.last_chunk_id = -1

        if not os.path.isdir(self.database_path):
            os.mkdir(self.database_path)

    def insert_sequences(self, sequences, chunksize=10) -> None:

        processed_sequences = 0

        h5_file = h5py.File(self.h5_file_name, 'w')
        h5_file_str_datatype = h5py.special_dtype(vlen=str)

        if self.database_metadata['slicesize'] is not None:
            sequences = slice_sequences(sequences, size=self.database_metadata['slicesize'], jump=self.database_metadata['jumpsize'])
        
        for chunk_id, sequence_chunk in enumerate(iter_chunks(sequences, chunksize), start=self.last_chunk_id+1):
            sequence_ids, sequence_vectors, sequence_raw = [], [], []

            for r, record in enumerate(sequence_chunk):
                
                ngrams_frame = self.model.compute_sequence_vector(str(record.seq))
                sequence_vectors.append(ngrams_frame)
                sequence_ids.append(record.id.encode('ascii', 'ignore'))
                sequence_raw.append(str(record.seq))
                self.database_metadata['records'] += 1

            sequence_vectors_array = np.array(sequence_vectors)

            normalized_sequence_vectors_array = sequence_vectors_array / np.linalg.norm(sequence_vectors_array, axis=1)[:, np.newaxis]
            normalized_sequence_vectors_array = normalized_sequence_vectors_array.astype(np.float32)
            normalized_sequence_vectors_array[~np.isfinite(normalized_sequence_vectors_array)] = 0
            
            if self.last_chunk_id == -1:

               h5_file.create_dataset('data', data=normalized_sequence_vectors_array, compression="gzip", chunks=True, maxshape=(None,self.model.config['vector_size']), dtype='float32')
               h5_file.create_dataset('ids', data=sequence_ids, compression="gzip", chunks=True, dtype=h5_file_str_datatype, maxshape=(None,)) 

            else:

                h5_file['data'].resize((h5_file['data'].shape[0] + normalized_sequence_vectors_array.shape[0]), axis=0)
                h5_file['data'][-normalized_sequence_vectors_array.shape[0]:] = normalized_sequence_vectors_array

                h5_file['ids'].resize((h5_file['ids'].shape[0] + len(sequence_ids)), axis=0)
                h5_file['ids'][-len(sequence_ids):] = sequence_ids

            self.last_chunk_id += 1
            processed_sequences += chunksize
            logging.info(f"{processed_sequences} sequences processed")
            
        return self.database_metadata['records']

    def find_sequences(self, sequences:np.array, k:int=10, threads=mp.cpu_count(), chunksize=10, mode='ah') -> pd.DataFrame:
        
        import tensorflow as tf
        import scann

        dataset = h5py.File(self.h5_file_name, "r")['data']
        dataset_ids = h5py.File(self.h5_file_name, "r")['ids']

        tf.config.threading.set_inter_op_parallelism_threads(threads)
        tf.config.threading.set_intra_op_parallelism_threads(threads)

        searcher = scann.scann_ops_pybind.builder(dataset, k, "dot_product").tree(
            num_leaves=int(np.sqrt(self.database_metadata['records'])),
            num_leaves_to_search=self.database_metadata['records']
        )
        
        if mode == 'score_ah':
            searcher = searcher.score_ah(2, anisotropic_quantization_threshold=0.2)
        else:
            searcher = searcher.score_brute_force()

        searcher.set_n_training_threads(threads)
        
        searcher = searcher.build()

        for sequence_chunk in iter_chunks(sequences, chunksize):

            if self.database_metadata['slicesize'] is not None:
                sequence_chunk = slice_sequences(sequence_chunk, size=self.database_metadata['slicesize'], jump=self.database_metadata['jumpsize'])

            query_ids = []
            query_vectors = []

            for record in sequence_chunk:
                vector = self.model.compute_sequence_vector(str(record.seq))
                query_ids.append(record.id)
                query_vectors.append(vector)

            query_vector_normalized = query_vectors / np.linalg.norm(query_vectors, axis=1)[:, np.newaxis]
            query_vector_normalized = query_vector_normalized.astype(np.float32)
            hits, distances = searcher.search_batched(query_vector_normalized)
            
            hit_ids_output   = []
            query_ids_output = []
            distances_output = []
            
            for q, query_id in enumerate(query_ids):
                for h, hit in enumerate(hits[q,:]): 
                    query_ids_output.append(query_id)
                    hit_ids_output.append(hit)
                    distances_output.append(distances[q][h])

            hit_ids_output_sorted = sorted(set(hit_ids_output))
            hit_def_output_sorted = dataset_ids[hit_ids_output_sorted]

            hdf_id_to_def  = dict(zip(hit_ids_output_sorted, hit_def_output_sorted))
            hit_def_output = [hdf_id_to_def[id].decode("utf-8")  for id in hit_ids_output]
            
            df_query_results = pd.DataFrame(
                {
                    'query':query_ids_output, 
                    'subject': hit_def_output, 
                    'cosine_similarity': distances_output
                }, columns=['query', 'subject', 'cosine_similarity']
            ).groupby(by=['query', 'subject']).max().sort_values(by=['query', 'cosine_similarity'], ascending=False).reset_index()

            yield df_query_results

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