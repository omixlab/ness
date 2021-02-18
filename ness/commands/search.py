from Bio import SeqIO
from scipy.spatial.distance import cosine
from ness.models import FastText
from Bio import pairwise2
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import json
import faiss
import time

def search(arguments):

    model = FastText.load(arguments.model)
    database_metadata = json.loads(open(f'{arguments.database}.meta.json').read())
    
    df_results = pd.DataFrame(columns=['query', 'subject', 'cosine_similarity'])

    for r, record in enumerate(SeqIO.parse(open(arguments.input), 'fasta')):

        df_query_results = pd.DataFrame(columns=['query', 'subject', 'cosine_similarity'])

        query_vectors = np.array(model.compute_sequence_vector(str(record.seq))).astype(np.float32)
        faiss.normalize_L2(query_vectors)
        query_hits = []

        for chunk_id in database_metadata['chunk_ids']:

            index = faiss.read_index(f'{arguments.model}.{chunk_id}.index')
            subject_ids = np.load(f'{arguments.model}.{chunk_id}.ids.npy')
            subject_seq = np.load(f'{arguments.model}.{chunk_id}.seq.npy')

            hits_distances, hits_indexes = index.search(query_vectors, arguments.hits)
            hits_indexes_adjusted = hits_indexes.reshape(-1, 1)[:,0]
            hits_distances_adjusted = hits_distances.reshape(-1, 1)[:,0]

            hits_ids = subject_ids[hits_indexes_adjusted]
            hits_seq = subject_seq[hits_indexes_adjusted]

            for h, hit_id in enumerate(hits_ids):
                
                df_query_results = df_query_results.append(
                    {'query': record.id, 'subject': hits_ids[h], 'cosine_similarity': 1 - hits_distances_adjusted[h]},
                    ignore_index=True
                )
                df_query_results = df_query_results.groupby(by=['query', 'subject']).max().reset_index()
    
        df_query_results = df_query_results.sort_values(by='cosine_similarity', ascending=False)
    
    df_results = pd.concat([df_results, df_query_results])
    df_results.to_csv(arguments.output, index=False)
