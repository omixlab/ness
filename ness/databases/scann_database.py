from __future__ import annotations
import os
os.environ['HDF5_USE_FILE_LOCKING'] = "FALSE"

from ness.databases import BaseDatabase
from ness.databases.utils import search_sequence_chunk_against_scann_database
from ness.models import BaseModel
from ness.models import load_model
from ness.utils.iteration import iter_chunks, slice_sequences
from functools import partial
import tensorflow as tf
import threading
import multiprocessing as mp
import time
import logging
import pandas as pd
import numpy as np
import json
import copy
import pickle
import os
from queue import Queue


__SCANN_INPUT_QUEUE__  = Queue()
__SCANN_OUTPUT_QUEUE__ = Queue()

__PARALLEL_SCANN__ = 0

QUEUE_TIMEOUT = 0.0001

def __query_scann_database__(h5_file, database_metadata, search_mode, k):

    import scann
    import h5py

    global __SCANN_INPUT_QUEUE__
    global __SCANN_OUTPUT_QUEUE__
    global __PARALLEL_SCANN__

    dataset = h5py.File(h5_file, "r")['data']
    dataset_ids = h5py.File(h5_file, "r")['ids']

    searcher = scann.scann_ops_pybind.builder(dataset, k, "dot_product").tree(
        num_leaves=int(np.sqrt(database_metadata['records'])),
        num_leaves_to_search=database_metadata['records']
    )
    
    if search_mode == 'score_ah':
        searcher = searcher.score_ah(2, anisotropic_quantization_threshold=0.2)
    else:
        searcher = searcher.score_brute_force()
    
    searcher = searcher.build()
    
    while True:
        
        try:
            input_data = __SCANN_INPUT_QUEUE__.get(timeout=QUEUE_TIMEOUT)
        except:
            input_data = None
        
        if input_data == 'STOP':
            break
        
        elif input_data is None:
            continue
        
        sequence_vector, sequence_id, sequence_raw = input_data
        hits, distances = searcher.search_batched([sequence_vector])
        output_data = [sequence_vector, sequence_id, sequence_raw, hits[0], distances[0]]
        __SCANN_OUTPUT_QUEUE__.put(output_data)

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

    def transform_sequences(self, sequences):

        if self.database_metadata['slicesize'] is not None or self.database_metadata['jumpsize'] is not None:
            return slice_sequences(sequences, size=self.database_metadata['slicesize'], jump=self.database_metadata['jumpsize'])
        else:
            return sequences

    def sequence_embedding(self, sequences):

        sequence_vectors = []
        sequence_ids     = []
        sequence_raw     = []

        for record in sequences:

            ngrams_frame = self.model.compute_sequence_vector(str(record.seq))
            sequence_vectors.append(ngrams_frame)
            sequence_ids.append(record.id.encode('ascii', 'ignore'))
            sequence_raw.append(str(record.seq))

        sequence_vectors = np.array(sequence_vectors)

        sequence_vectors = sequence_vectors / np.linalg.norm(sequence_vectors, axis=1)[:, np.newaxis]
        sequence_vectors = sequence_vectors.astype(np.float32)
        sequence_vectors[~np.isfinite(sequence_vectors)] = 0

        return sequence_vectors, sequence_ids, sequence_raw

    def insert_sequences(self, sequences, chunksize=10) -> None:

        import h5py

        processed_sequences = 0

        h5_file = h5py.File(self.h5_file_name, 'w')
        h5_file_str_datatype = h5py.special_dtype(vlen=str)

        sequences = self.transform_sequences(sequences)

        for chunk_id, sequence_chunk in enumerate(iter_chunks(sequences, chunksize), start=self.last_chunk_id+1):

            sequences_vectors, sequences_ids, sequences_raw = self.sequence_embedding(sequence_chunk)
            self.database_metadata['records'] += len(set(sequences_ids))

            if self.last_chunk_id == -1:

               h5_file.create_dataset('data', data=sequences_vectors, compression="gzip", chunks=True, maxshape=(None,self.model.config['vector_size']), dtype='float32')
               h5_file.create_dataset('ids', data=sequences_ids, compression="gzip", chunks=True, dtype=h5_file_str_datatype, maxshape=(None,)) 
               h5_file.create_dataset('raw', data=sequences_raw, compression="gzip", chunks=True, dtype=h5_file_str_datatype, maxshape=(None,)) 

            else:

                h5_file['data'].resize((h5_file['data'].shape[0] + sequences_vectors.shape[0]), axis=0)
                h5_file['data'][-sequences_vectors.shape[0]:] = sequences_vectors
                h5_file['ids'].resize((h5_file['ids'].shape[0] + len(sequences_ids)), axis=0)
                h5_file['ids'][-len(sequences_ids):] = sequences_ids
                h5_file['raw'].resize((h5_file['raw'].shape[0] + len(sequences_raw)), axis=0)
                h5_file['raw'][-len(sequences_raw):] = sequences_raw

            self.last_chunk_id += 1
            processed_sequences += len(set(sequences_ids))
            logging.info(f"{processed_sequences} sequences processed")

    def find_sequences(self, sequences, k:int=10, threads=mp.cpu_count(), chunksize=100, mode='ah') -> pd.DataFrame:

        import scann
        import h5py
        
        global __SCANN_INPUT_QUEUE__
        global __SCANN_OUTPUT_QUEUE__

        INPUT_COUNT  = 0
        OUTPUT_COUNT = 0

        idx2id = {idx:id for idx,id in enumerate(h5py.File(self.h5_file_name, "r")['ids'])}

        sequences = self.transform_sequences(sequences)

        THREAD_LIST = [threading.Thread(target=__query_scann_database__, args=(self.h5_file_name, self.database_metadata, mode, k)) for _ in range(threads)]

        for THREAD in THREAD_LIST:
            THREAD.start()

        for sequence_chunk in iter_chunks(sequences, chunksize):

            sequences_vectors, sequences_ids, sequences_raw = self.sequence_embedding(sequence_chunk)

            for sequence_data in zip(sequences_vectors, sequences_ids, sequences_raw):
                __SCANN_INPUT_QUEUE__.put(sequence_data)
                INPUT_COUNT += 1

        print(len(THREAD_LIST))

        for _ in THREAD_LIST:
            __SCANN_INPUT_QUEUE__.put('STOP')

        output_data = []
        
        while True:
            if INPUT_COUNT == OUTPUT_COUNT:
                break
            df_results = pd.DataFrame()
            try:
                scann_output = __SCANN_OUTPUT_QUEUE__.get(timeout=QUEUE_TIMEOUT)
            except:
                continue
            if scann_output is None:
                continue
            _, sequence_id, _, hits, distances = scann_output
            OUTPUT_COUNT += 1

            for hit, distance in zip(hits, distances):
                output_data.append({'query_id': sequence_id, 'hit_id':idx2id[hit], 'similarity':distance})
            
            yield pd.DataFrame(output_data)

        for THREAD in THREAD_LIST:
            THREAD.join()
           
        yield pd.DataFrame([])

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
    

