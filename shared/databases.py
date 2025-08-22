from abc import ABC
from typing import Generic, TypeVar, Type, List, Optional
from pydantic import BaseModel
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions, ContainerProxy

T = TypeVar("T", bound=BaseModel)

class AsyncCosmosRepository(Generic[T], ABC):
    """
    Async generic Cosmos “repository”:
     - connects via connection string
     - optionally bootstraps database+container
     - exposes async create/read/update/delete/query
    """
    def __init__(self,connection_string: str,database_name: str,container_name: str,model_cls: Type[T],partition_key_path: str = "/id",create_if_not_exists: bool = False):
        # note: don't await in __init__; client is ready to use
        self.client = CosmosClient.from_connection_string(connection_string)
        self.database_name = database_name
        self.container_name = container_name
        self.partition_key_path = partition_key_path
        self.create_if_not_exists = create_if_not_exists
        self.model_cls = model_cls
        self.container: Optional[ContainerProxy] = None

    async def init_container(self):
        """Call this once before using CRUD methods (e.g. at app startup)."""
        if self.create_if_not_exists:
            # ensure DB exists
            await self.client.create_database_if_not_exists(id=self.database_name)
            db = self.client.get_database_client(self.database_name)
            # ensure container exists
            await db.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path=self.partition_key_path),
            )
        self.container = self.client.get_database_client(self.database_name).get_container_client(self.container_name)

    async def create(self, item: T) -> T:
        if not self.container:
            await self.init_container()
        created_raw = await self.container.create_item(item.model_dump())
        await self.close()
        return self.model_cls.model_validate(created_raw)

    async def get(self, id: str, partition_key: str) -> Optional[T]:
        if not self.container:
            await self.init_container()
        try:
            raw = await self.container.read_item(id, partition_key)
            await self.close()
            return self.model_cls.model_validate(raw)
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def update(self, item: T) -> T:
        if not self.container:
            await self.init_container()
        upserted = await self.container.upsert_item(item.model_dump())
        await self.close()
        return self.model_cls.model_validate(upserted)

    async def delete(self, id: str, partition_key: str) -> None:
        if not self.container:
            await self.init_container()
        await self.container.delete_item(id, partition_key)
        await self.close()

    async def query(self,query: str,parameters: List[dict] = None) -> List[T]:
        if not self.container:
            await self.init_container()
        # Pass everything except the query itself as keyword args
        docs_iter = self.container.query_items(
            query=query,
            parameters=parameters or []
        )

        results: List[T] = []
        # query_items returns an async iterator
        async for doc in docs_iter:
            results.append(self.model_cls.model_validate(doc))
        await self.close()
        return results

    async def close(self) -> None:
        """Call this when you’re completely done with the client."""
        await self.client.close()