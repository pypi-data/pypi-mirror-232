import tiktoken
import hashlib
import numpy as np
from numpy.linalg import norm
from typing import List


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_hash_from_string(string: str) -> str:
    return hashlib.sha256(string.encode()).hexdigest()


def cosine_similarity(embedding_a: List[float], embedding_b: List[float]) -> float:
    return np.dot(embedding_a, embedding_b) / (norm(embedding_a) * norm(embedding_b))


def get_chunk_indices_by_distance(
    question_embedding: List[float], chunk_embeddings: List[List[float]]
) -> List[int]:
    """
    Retrieve the indices of the chunk embeddings based on their cosine similarity with a given question embedding.

    Parameters:
    - question_embedding (List[float]): The embedding of the question.
    - chunk_embeddings (List[List[float]]): A list of embeddings of the chunks.

    Returns:
    - List[int]: A list of indices sorted in decreasing order based on their
    cosine similarity with the question embedding.
    """
    ans = [
        (i, cosine_similarity(question_embedding, emb))
        for i, emb in enumerate(chunk_embeddings)
    ]
    ans.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in ans]
