from .base_database import BaseDatabase
from ness.utils.iteration import iter_chunks
import pandas as pd
import numpy as np
import h5py
import os
import json

def load_database(file_name:str) -> BaseDatabase:

    from ness.databases import databases

    config_file_name = os.path.join(file_name, 'database.json')
    assert os.path.isfile(config_file_name)
    
    config = json.loads(open(config_file_name).read())
    database_type = config['database_type']
    return databases[database_type].load(file_name)

def search_sequence_chunk_against_scann_database(sequences, h5_file, database_metadata, model, search_mode, k):

    import tensorflow as tf
    import scann

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

    for sequence_chunk in iter_chunks(sequences, chunksize):

        if self.database_metadata['slicesize'] is not None:
            sequence_chunk = slice_sequences(sequence_chunk, size=self.database_metadata['slicesize'], jump=self.database_metadata['jumpsize'])

        query_ids = []
        query_vectors = []

        for record in sequence_chunk:
            vector = model.compute_sequence_vector(str(record.seq))
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
        
        return pd.DataFrame(
            {
                'query':query_ids_output, 
                'subject': hit_def_output, 
                'cosine_similarity': distances_output
            }, columns=['query', 'subject', 'cosine_similarity']
        ).groupby(by=['query', 'subject']).max().sort_values(by=['query', 'cosine_similarity'], ascending=False).reset_index() 
