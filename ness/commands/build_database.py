from Bio import SeqIO
from argparse import Namespace
from ness.models import FastText
import numpy as np
import json
import faiss


def build_database(arguments:Namespace):

    model = FastText.load(arguments.model)
    database_metadata = {'records': 0, 'chunk_ids': []}
    sequence_ids, sequence_vectors, sequence_raw, chunk_id = [], [], [], 0

    for r, record in enumerate(SeqIO.parse(open(arguments.input), 'fasta')):

        for ngrams_frame in model.compute_sequence_vector(str(record.seq)):
            sequence_vectors.append(ngrams_frame)
            sequence_ids.append(record.id)
            sequence_raw.append(str(record.seq))
            break

        if r % arguments.records_per_chunk == 0 and r > 0:
            database_metadata['chunk_ids'].append(chunk_id)
            save_database_chunk(
                output_basename=arguments.output, 
                chunk_id=chunk_id, 
                sequence_ids=sequence_ids, 
                sequence_vectors=sequence_vectors,
                sequence_raw=sequence_raw,
                database_metadata=database_metadata
            )
            sequence_ids, sequence_vectors, sequence_raw, chunk_id = [], [], [], chunk_id + 1

        if r % 1000 == 0 and r > 0:
            print(r, 'sequences already processed ...')
        
    if len(sequence_vectors) > 0:
        database_metadata['chunk_ids'].append(chunk_id)
        save_database_chunk(
            output_basename=arguments.output, 
            chunk_id=chunk_id, 
            sequence_ids=sequence_ids, 
            sequence_vectors=sequence_vectors,
            sequence_raw=sequence_raw,
            database_metadata=database_metadata
        )


def save_database_chunk(output_basename, chunk_id, sequence_ids, sequence_vectors, sequence_raw, database_metadata):

    database_metadata['chunk_ids'].append(chunk_id)
    index, sequence_vectors = create_faiss_index(sequence_vectors)
    faiss.write_index(index, f'{output_basename}.{chunk_id}.index')
    
    np.save(f'{output_basename}.{chunk_id}.ids',  np.array(sequence_ids))

    with open(f'{output_basename}.meta.json', 'w') as writer:
        writer.write(json.dumps(database_metadata))


def create_faiss_index(sequence_vectors):

    sequence_vectors = np.array(sequence_vectors).astype(np.float32)
    index = faiss.IndexFlatIP(sequence_vectors.shape[1])
    faiss.normalize_L2(sequence_vectors)
    index.train(sequence_vectors)
    index.add(sequence_vectors)

    return index, sequence_vectors