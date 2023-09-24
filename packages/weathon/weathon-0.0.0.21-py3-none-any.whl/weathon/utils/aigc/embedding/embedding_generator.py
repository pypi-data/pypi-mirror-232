from typing import List
from numpy import ndarray
from sentence_transformers import SentenceTransformer
from semantic_kernel.connectors.ai.embeddings.embedding_generator_base import EmbeddingGeneratorBase


class EmbeddingGenerator(EmbeddingGeneratorBase):
    def __init__(self, model_name_or_path: str = 'models/moka-ai/m3e-base', device="cpu", normalize_embeddings=False) -> None:
        self.normalize_embeddings = normalize_embeddings
        self.embeddings = SentenceTransformer(model_name_or_path=model_name_or_path, device=device)

    async def generate_embeddings_async(self, texts: List[str]) -> ndarray:
        return self.embeddings.encode(sentences=texts, normalize_embeddings=self.normalize_embeddings)

    def generate_embeddings(self, texts: List[str]) -> ndarray:
        return self.embeddings.encode(sentences=texts, normalize_embeddings=self.normalize_embeddings)
