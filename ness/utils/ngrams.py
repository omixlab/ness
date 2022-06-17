def split_ngrams(sequence:str, ksize:int=3, both_strands=False):

    from Bio.Seq import reverse_complement
    
    sequences = [sequence]

    if both_strands:
        sequences.append(reverse_complement(sequence))

    ngrams = []

    for sequence in sequences:
        ngrams.append([])

        for n in range(0, len(sequence), 1):
            ngram = sequence[n:n+ksize]
            if len(ngram) == ksize:
                ngrams[-1].append(str(ngram))

    return ngrams