import openai
import json
from typing import List, Dict, Any


class OpenAIWrapper:
    """
    Wrapper for the OpenAI API, providing methods for obtaining embeddings and chat completions.

    Attributes:
    chat_deployment (str): The deployment ID for the chat model.
    embedding_deployment (str): The deployment ID for the embedding model.
    chat_model (str): The specific model ID for the chat function (default is 'gpt-35-turbo').
    embedding_model (str): The specific model ID for the embedding function (default is 'text-embedding-ada-002').

    Methods:
    get_embedding(query: str) -> List[float]: Retrieves the embedding for a single query.
    get_embeddings(chunks: List[str]) -> List[List[float]]: Retrieves the embeddings for a list of text chunks.
    get_chat_completion(sys_prompt: str, user_prompt: str) -> Dict[str, Any]:
        Obtains a chat completion for a system and user prompt.

    Note:
    The API key and other configurations should be set before using the methods.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        chat_deployment: str,
        embedding_deployment: str,
        api_type: str = "azure",
        api_version: str = "2023-08-01-preview",
    ):
        openai.api_key = api_key
        openai.api_base = endpoint
        openai.api_type = api_type
        openai.api_version = api_version

        self.chat_deployment = chat_deployment
        self.embedding_deployment = embedding_deployment

        self.chat_model = "gpt-35-turbo"
        self.embedding_model = "text-embedding-ada-002"

    def get_embedding(self, query: str) -> List[float]:
        response = openai.Embedding.create(
            model=self.embedding_model,
            deployment_id=self.embedding_deployment,
            input=query,
        )
        return response["data"][0]["embedding"]

    def get_embeddings(self, chunks: List[str]) -> List[List[float]]:
        # Did some quick testing to see if rate limit is a thing here, doesn't seem like it with a sane document
        # Currently no handling
        embeddings = []
        for i in range(0, len(chunks), 16):
            response = openai.Embedding.create(
                model=self.embedding_model,
                deployment_id=self.embedding_deployment,
                input=chunks[i : i + 16],
            )
            embeddings += [item["embedding"] for item in response["data"]]
        return embeddings

    def get_chat_completion(self, sys_prompt: str, user_prompt: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = openai.ChatCompletion.create(
            deployment_id=self.chat_deployment,
            model=self.chat_model,
            messages=messages,
            temperature=0,
        )

        # TODO: wellicht wat handling van slechte response
        resp_msg = response["choices"][0]["message"]

        answer_json = json.loads(resp_msg["content"])

        return answer_json
