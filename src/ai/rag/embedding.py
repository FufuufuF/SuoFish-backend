from typing import List
from openai import OpenAI

from src.core.config import embedding as embedding_config

class Embedding():
    
    def __init__(self):
        self.client = OpenAI(
            api_key=embedding_config.api_key,
            base_url=embedding_config.base_url,
        )
        self.mode_name = embedding_config.model_name

    def embed_text(self, chunk: str) -> List[float]:
        completion = self.client.embeddings.create(
            model=self.mode_name,
            input=chunk,
        )
        return completion.data[0].embedding

    def embed_texts(self, chunks: List[str]) -> List[List[float]]:
        return [self.embed_text(chunk) for chunk in chunks]
