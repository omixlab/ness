def split_ngrams(sequence:str, ksize:int=3):
    
    ngrams = []

    for k in range(ksize):
        ngrams.append([])
        sequence_trimmed = sequence[k::]

        for n in range(0, len(sequence_trimmed), ksize):
            ngram = sequence_trimmed[n:n+ksize]
            if len(ngram) == ksize:
                ngrams[-1].append(ngram)

    return ngrams