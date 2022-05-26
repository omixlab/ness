def iter_chunks(items, size):
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk

def slice_sequences(sequences, size=100):
    for sequence in sequences:
        for i in range(0, len(sequence) - size + 1):
            yield sequence[i:i+size]