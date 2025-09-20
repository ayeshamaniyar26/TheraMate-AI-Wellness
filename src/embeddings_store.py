# embeddings_store.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

EMB_MODEL_NAME = "all-MiniLM-L6-v2"  # compact, fast for demo
VECTOR_PATH = "data/faiss_index.pkl"
META_PATH = "data/faiss_meta.pkl"

class EmbeddingsStore:
    def __init__(self, model_name=EMB_MODEL_NAME, dim=384):
        self.model = SentenceTransformer(model_name)
        self.dim = dim
        self.index = None
        self.meta = []

    def build_from_texts(self, texts:list):
        embs = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        index = faiss.IndexFlatIP(embs.shape[1])
        faiss.normalize_L2(embs)
        index.add(embs)
        self.index = index
        self.meta = texts
        self.save()

    def search(self, query:str, topk=5):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, topk)
        results = []
        for idx in I[0]:
            results.append(self.meta[idx])
        return results

    def save(self):
        with open(VECTOR_PATH, "wb") as f:
            pickle.dump(self.index, f)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.meta, f)

    def load(self):
        import pickle
        with open(VECTOR_PATH, "rb") as f:
            self.index = pickle.load(f)
        with open(META_PATH, "rb") as f:
            self.meta = pickle.load(f)
