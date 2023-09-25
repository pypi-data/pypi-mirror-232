import struct
import base64
from typing import List
from pydantic import BaseModel
from azure.cosmos import CosmosClient
from promptflow_helpers.chunker import ChunkInfo


class CosmosChunkInfo(BaseModel):
    startCursor: int
    endCursor: int
    numTokens: int
    embedding: List[float]


class CosmosChunkMetaInfo(BaseModel):
    wantedTokens: int
    sentenceOverlap: int
    chunkOverlap: int
    encoding: str

    def get_meta_setting_string(self) -> str:
        return f"{self.wantedTokens}-{self.sentenceOverlap}-{self.chunkOverlap}-{self.encoding}"


class CosmosChunkItem(BaseModel):
    """
    Pydantic dataclass representing an item in CosmosDB.
    """

    id: str
    documentId: str
    metaInfo: CosmosChunkMetaInfo
    chunkInfo: CosmosChunkInfo


class EncryptedEmbeddingException(Exception):
    pass


class CosmosDB:
    """
    CosmosDB handler class for performing operations on Azure CosmosDB.

    This class provides a simple interface to interact with CosmosDB by leveraging the CosmosClient
    from the `azure.cosmos` module. The primary goal is to save, prepare and retrieve chunk items
    in the CosmosDB.

    Attributes:
    - client: The CosmosClient used to communicate with the CosmosDB service.
    - database: Reference to the CosmosDB database.
    - container: Reference to the container within the CosmosDB database.

    Methods:
    - _get_partition_key_string: Helper method to generate partition key string based on meta info and doc_id.
    - prepare_chunk_items: Converts given chunk information into CosmosChunkItem list.
    - save_chunk_item: Save a single chunk item into CosmosDB.
    - get_chunk_items: Retrieve chunk items from CosmosDB based on meta information and doc_id.
    """

    def __init__(
        self, endpoint: str, api_key: str, database_name: str, container_name: str
    ):
        self.client = CosmosClient(url=endpoint, credential=api_key)
        self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)

    @staticmethod
    def _get_partition_key_string(meta_info: CosmosChunkMetaInfo, doc_id: str) -> str:
        return f"{meta_info.get_meta_setting_string()}-{doc_id}"

    @staticmethod
    def prepare_chunk_items(
        doc_id: str,
        meta_info: CosmosChunkMetaInfo,
        chunk_infos: List[ChunkInfo],
        embeddings: List[List[float]],
    ) -> List[CosmosChunkItem]:
        """
        Convert the given chunk information into a list of CosmosChunkItem.

        Args:
            doc_id (str): Document ID.
            meta_info (CosmosChunkMetaInfo): Metadata information of the chunk.
            chunk_infos (List[ChunkInfo]): List of chunk information.
            embeddings (List[List[float]]): List of embeddings.

        Returns:
            List[CosmosChunkItem]: A list of CosmosChunkItem created from
            provided chunk information and embeddings.
        """
        assert len(chunk_infos) == len(embeddings)

        cosmos_chunk_items: List[CosmosChunkItem] = []

        for i in range(len(chunk_infos)):
            chunk_info = chunk_infos[i]

            cosmos_chunks_info = CosmosChunkInfo(
                startCursor=chunk_info.start_cursor,
                endCursor=chunk_info.end_cursor,
                numTokens=chunk_info.num_tokens,
                embedding=embeddings[i],
            )

            cosmos_chunk_item = CosmosChunkItem(
                id=str(chunk_info.chunk_index),
                documentId=CosmosDB._get_partition_key_string(meta_info, doc_id),
                metaInfo=meta_info,
                chunkInfo=cosmos_chunks_info,
            )

            cosmos_chunk_items.append(cosmos_chunk_item)

        return cosmos_chunk_items

    @staticmethod
    def _encode_embedding(embedding: List[float]) -> str:
        """
        Encode a list of floats (embedding) into a base64 encoded string.

        Args:
            embedding (List[float]): List of floats to be encoded.

        Returns:
            str: The base64 encoded string representation of the embedding.
        """
        buf = bytes()
        for item in embedding:
            buf += struct.pack("f", item)
        base64_encoded = base64.b64encode(buf)
        base64_encoded_string = base64_encoded.decode("ascii")
        return base64_encoded_string

    @staticmethod
    def _decode_embedding(encoded_embedding_string: str) -> List[float]:
        """
        Decode a base64 encoded embedding string back into a list of floats.

        Args:
            encoded_embedding_string (str): The base64 encoded string representation of the embedding.

        Returns:
            List[float]: The decoded list of floats (embedding).
        """
        base64_encoded = encoded_embedding_string.encode("ascii")
        embedding_bytes = base64.b64decode(base64_encoded)
        unpacked: List[float] = []
        for i in range(0, len(embedding_bytes), 4):
            unpacked += struct.unpack("f", embedding_bytes[i : i + 4])
        return unpacked

    def save_chunk_item(self, chunk_item: CosmosChunkItem) -> None:
        # if isinstance(chunk_item.chunkInfo.embedding, str):
        #     raise EncryptedEmbeddingException

        # chunk_item.chunkInfo.embedding = self._encode_embedding(
        #     chunk_item.chunkInfo.embedding
        # )
        self.container.create_item(chunk_item.dict())

    def get_chunk_items(
        self, meta_info: CosmosChunkMetaInfo, doc_id: str
    ) -> List[CosmosChunkItem]:
        resp = self.container.query_items(
            query=f"SELECT * FROM c WHERE c.documentId='{self._get_partition_key_string(meta_info, doc_id)}'"
        )

        # for item in resp:
        #     item["chunkInfo"]["embedding"] = self._decode_embedding(
        #         item["chunkInfo"]["embedding"]
        #     )

        chunk_items = [CosmosChunkItem(**item) for item in resp]

        return chunk_items
