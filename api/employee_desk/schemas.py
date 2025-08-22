from pydantic import BaseModel, Field
from shared.databases import AsyncCosmosRepository
from shared.schemas import ChatResponse

class EmployeeQueryRewriter(BaseModel):
    search_query: str = Field(description='The refined or rewritten query for improved relevance')

class EmployeeQueryResponse(BaseModel):
    answer: str = Field(description='The response to the employee query based on company policies')
    followup_questions: list[str] = Field(description='Exactly 3 new follow-up questions related to the context')

class EmployeeConfig(BaseModel):
    """Configuration for employee desk, extending BaseDeskConfig with employee-specific fields."""
    id: str = Field(description="UUID of the company")
    org_id: str = Field(description="Organization's unique ID")
    org_name: str = Field(description="Organization's full name")
    query: str = Field(description="Query topics for employee assistance")
    about: str = Field(description="Information about the organization or configuration")
    index_name: str = Field(description="Name of the search index", default="")

class EmployeeConfigRepository(AsyncCosmosRepository[EmployeeConfig]):
    def __init__(self, conn_str: str):
        super().__init__(
            connection_string=conn_str,
            database_name="employee_desk",
            container_name="company_configs",
            model_cls=EmployeeConfig,
            partition_key_path="/org_id",
            create_if_not_exists=True,
        )

    async def find_by_org_id(self, org_id: str) -> list[EmployeeConfig]:
        sql = "SELECT * FROM c WHERE c.org_id = @org_id"
        params = [{"name": "@org_id", "value": org_id}]
        return await self.query(sql, params)

class EmployeeChatResponseRepository(AsyncCosmosRepository[ChatResponse]):
    def __init__(self, conn_str: str):
        super().__init__(
            connection_string=conn_str,
            database_name="employee_desk",
            container_name="chat_responses",
            model_cls=ChatResponse,
            partition_key_path="/conversation_id",
            create_if_not_exists=True,
        )


