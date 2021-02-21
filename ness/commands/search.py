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
    faiss.omp_set_num_threads(arguments.threads)
    
    df_results = pd.DataFrame(columns=['query', 'subject', 'cosine_similarity'])

    for r, record in enumerate(SeqIO.parse(open(arguments.input), 'fasta')):

        #print(f'[{r}] processing', record.id, '...')

        df_query_results = pd.DataFrame(columns=['query', 'subject', 'cosine_similarity'])

        query_vectors = np.array([model.compute_sequence_vector(str(record.seq))[0]]).astype(np.float32)
        faiss.normalize_L2(query_vectors)
        loaded_index_chunk_id = None

        for chunk_id in database_metadata['chunk_ids']:

            if chunk_id != loaded_index_chunk_id:
                subject_ids = np.load(f'{arguments.database}.{chunk_id}.ids.npy')
                index = faiss.read_index(f'{arguments.database}.{chunk_id}.index')
                loaded_index_chunk_id = chunk_id

            hits_distances, hits_indexes = index.search(query_vectors, arguments.hits)
            hits_indexes_adjusted = hits_indexes.reshape(-1, 1)[:,0]
            hits_distances_adjusted = hits_distances.reshape(-1, 1)[:,0]

            hits_ids = subject_ids[hits_indexes_adjusted]

            for h, hit_id in enumerate(hits_ids):
                
                df_query_results = df_query_results.append(
                    {'query': record.id, 'subject': hits_ids[h], 'cosine_similarity': hits_distances_adjusted[h]},
                    ignore_index=True
                )
                
        df_query_results = df_query_results.groupby(by=['query', 'subject']).max().reset_index().sort_values(by='cosine_similarity', ascending=False).head(arguments.hits) 
        df_query_results.to_csv(arguments.output, index=False, header=True if r == 0 else False, mode='w' if r == 0 else 'a')
