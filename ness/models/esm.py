from __future__ import annotations
import torch
import esm
from .base_model import BaseModel
from ness.utils.fasta import FASTANgramIterator
import numpy as np
import pickle
import json

class ESM1(BaseModel):

    def __init__(self):
        
        self.model = None
        self.config = {'model_type': 'esm'}   
    
    def build_model(self) -> None:

        self.model, self.alphabet = esm.pretrained.esm2_t33_650M_UR50D()
        self.batch_converter = self.alphabet.get_batch_converter()
        self.model.eval()  # disables dropout for deterministic results

    def compute_sequence_vector(self, sequence:str) -> None:

        data = [("sequence", sequence)]
    
        _, _, batch_tokens = self.batch_converter(data)
        batch_lens = (batch_tokens != self.alphabet.padding_idx).sum(1)

        with torch.no_grad():
            results = self.model(batch_tokens, repr_layers=[33], return_contacts=True)
        token_representations = results["representations"][33]
        sequence_representations = []
        for i, tokens_len in enumerate(batch_lens):
            sequence_representations.append(token_representations[i, 1 : tokens_len - 1].mean(0))
        sequence_representations = [t.numpy() for t in sequence_representations]
        return sequence_representations
