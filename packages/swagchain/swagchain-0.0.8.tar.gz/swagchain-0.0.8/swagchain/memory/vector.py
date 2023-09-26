"""Swagchain `vector` module: A mini sdk of Pinecone's vector database API."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import (Any, Dict, Generic, Iterable, List, Literal, TypeAlias,
                    TypeVar, Union, cast)
from uuid import uuid4

from aiohttp import ClientSession
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

Vector: TypeAlias = List[Union[int, float]]
Value: TypeAlias = Union[int, float, str, bool, List[str]]
QueryJoin: TypeAlias = Literal["$and", "$or"]
QueryWhere: TypeAlias = Literal[
    "$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"
]
QueryKey: TypeAlias = Union[str, QueryWhere, QueryJoin]
QueryValue: TypeAlias = Union[Value, List[Value], "Query", List["Query"]]
Query: TypeAlias = Dict[QueryKey, QueryValue]
MetaData: TypeAlias = Dict[str, Value]
# Please write Sphinx documentation for this m

T = TypeVar("T")

class LazyProxy(Generic[T], ABC):
    def __init__(self) -> None:
        self.__proxied: T | None = None

    def __getattr__(self, attr: str) -> object:
        return getattr(self.__get_proxied__(), attr)

    def __repr__(self) -> str:
        return repr(self.__get_proxied__())

    def __str__(self) -> str:
        return str(self.__get_proxied__())

    def __dir__(self) -> Iterable[str]:
        return self.__get_proxied__().__dir__()

    def __get_proxied__(self) -> T:
        proxied = self.__proxied
        if proxied is not None:
            return proxied

        self.__proxied = proxied = self.__load__()
        return proxied

    def __set_proxied__(self, value: T) -> None:
        self.__proxied = value

    def __as_proxied__(self) -> T:
        """Helper method that returns the current proxy, typed as the loaded object"""
        return cast(T, self)

    @abstractmethod
    def __load__(self) -> T:
        ...



class QueryBuilder(object):
    
    def __init__(self, field: str = None, query: Query = None):  # type: ignore
        """
        Initializes a new QueryBuilder instance.

        Args:
            field (str, optional): The field to query. Defaults to None.
            query (Query, optional): The query dictionary. Defaults to an empty dictionary.
        """
        self.field = field
        self.query = query if query else {}

    def __repr__(self) -> str:
        """Returns the string representation of the query."""
        return f"{self.query}"

    def __call__(self, field_name: str) -> QueryBuilder:
        """
        Creates a new QueryBuilder instance with a given field name.

        Args:
            field_name (str): The field name to query.

        Returns:
            QueryBuilder: A new QueryBuilder instance.
        """
        return QueryBuilder(field_name)

    def __and__(self, other: QueryBuilder) -> QueryBuilder:
        """
        Combines two queries using the $and operator.

        Args:
            other (QueryBuilder): Another QueryBuilder instance.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.
        """
        return QueryBuilder(query={"$and": [self.query, other.query]})

    def __or__(self, other: QueryBuilder) -> QueryBuilder:
        """
        Combines two queries using the $or operator.

        Args:
            other (QueryBuilder): Another QueryBuilder instance.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.
        """
        return QueryBuilder(query={"$or": [self.query, other.query]})

    def __eq__(self, value: Value) -> QueryBuilder:  # type: ignore
        """
        Creates a new QueryBuilder instance with the $eq operator.

        Args:
            value (Value): The value to query.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.
        
        """
        return QueryBuilder(query={self.field: {"$eq": value}})

    def __ne__(self, value: Value) -> QueryBuilder:  # type: ignore
        """
        Creates a new QueryBuilder instance with the $ne operator.

        Args:
            value (Value): The value to query.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.
        
        """
        return QueryBuilder(query={self.field: {"$ne": value}})

    def __lt__(self, value: Value) -> QueryBuilder:
        """
        Creates a new QueryBuilder instance with the $lt operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.
        
        
        """
        
        return QueryBuilder(query={self.field: {"$lt": value}})

    def __le__(self, value: Value) -> QueryBuilder:
        """
        Creates a new QueryBuilder instance with the $lte operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$lte": value}})

    def __gt__(self, value: Value) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $gt operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """
        
        return QueryBuilder(query={self.field: {"$gt": value}})

    def __ge__(self, value: Value) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $gte operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.
        
        """
        
        
        return QueryBuilder(query={self.field: {"$gte": value}})

    def in_(self, values: List[Value]) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $in operator.

        Args:

            values (List[Value]): The values to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """
            
        return QueryBuilder(query={self.field: {"$in": values}})

    def nin_(self, values: List[Value]) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $nin operator.

        Args:

            values (List[Value]): The values to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$nin": values}})

class UpsertRequest(BaseModel):
    """
    A request to upsert a vector.

    Args:
        id (str, optional): The ID of the vector. Defaults to a random UUID.
        values (Vector): The vector values.
        metadata (MetaData): The vector metadata.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    values: Vector = Field(...)
    metadata: MetaData = Field(...)


class Embedding(BaseModel):
    """

    A vector embedding.

    Args:

        values (Vector): The vector values.

        metadata (MetaData): The vector metadata.

    """


    values: Vector = Field(...)
    metadata: MetaData = Field(...)


class QueryRequest(BaseModel):
    """
    A request to query vectors.

    Args:

        topK (int, optional): The number of results to return. Defaults to 10.

        filter (Query): The query filter.

        includeMetadata (bool, optional): Whether to include metadata in the response. Defaults to True.

        vector (Vector): The vector to query.

    """
    topK: int = Field(default=10)
    filter: Dict[str, Any] = Field(...)
    includeMetadata: bool = Field(default=True)
    vector: Vector = Field(...)


class QueryMatch(BaseModel):
    """

    A query match.

    Args:

        id (str): The ID of the vector.

        score (float): The match score.

        metadata (MetaData): The vector metadata.

    """  
    
    id: str = Field(...)
    score: float = Field(...)
    metadata: MetaData = Field(...)


class QueryResponse(BaseModel):
    """

    A response to a query request.

    Args:

        matches (List[QueryMatch]): The query matches.

    """   
    matches: List[QueryMatch] = Field(...)


class UpsertResponse(BaseModel):
    """

    A response to an upsert request.

    Args:

        upsertedCount (int): The number of vectors upserted.

    """ 
    
    upsertedCount: int = Field(...)


class VectorClient(LazyProxy[ClientSession]):
    """

    A client for the vector database.

    Args:

        api_key (str): The API key.

        api_endpoint (str): The API endpoint.

    """
    def __init__(self, api_key: str=os.environ.get("PINECONE_API_KEY"), api_endpoint: str=os.environ.get("PINECONE_API_URL")) -> None:  # type: ignore
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        super().__init__()

    def __load__(self) -> ClientSession:
        """

        Loads the client session.

        Returns:

            ClientSession: The client session.

        """
               
        return ClientSession(
            headers={"api-key": self.api_key},
            base_url=self.api_endpoint,
        )

    async def upsert(self, embeddings: List[Embedding]) -> UpsertResponse:
        """

        Upserts a list of vector embeddings.

        Args:

            embeddings (List[Embedding]): The vector embeddings.

        Returns:

            UpsertResponse: The upsert response.

        """        
        async with self.__load__() as session:
            values: List[Vector] = []
            metadata: List[MetaData] = []
            for embedding in embeddings:
                values.append(embedding.values)
                metadata.append(embedding.metadata)

            async with session.post(
                "/vectors/upsert",
                json={
                    "vectors": [
                        UpsertRequest(values=values, metadata=metadata).dict()
                        for values, metadata in zip(values, metadata)
                    ]
                },
            ) as response:
                return UpsertResponse(**await response.json())

    async def query(
        self, expr: Query, vector: Vector, topK: int, includeMetadata: bool = True
    ) -> QueryResponse:
        """

        Queries the vector database.

        Args:

            expr (Query): The query expression.

            vector (Vector): The vector to query.

            topK (int): The number of results to return.

            includeMetadata (bool, optional): Whether to include metadata in the response. Defaults to True.

        Returns:

            QueryResponse: The query response.

        """

        async with self.__load__() as session:
            payload = QueryRequest(
                topK=topK,
                filter=expr,  # type: ignore
                vector=vector,
                includeMetadata=includeMetadata,
            ).dict()
            async with session.post(
                "/query",
                json=payload,
            ) as response:
                return QueryResponse(**await response.json())