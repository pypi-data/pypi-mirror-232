from pydantic import BaseModel, Field


class HTTPError(BaseModel):
    detail: str = Field(example="HTTPException raised.")
