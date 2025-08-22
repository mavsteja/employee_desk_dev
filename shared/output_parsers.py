from pydantic import BaseModel

async def pydantic_dict_output_parser(schema:BaseModel) -> dict:
    return schema.model_dump()