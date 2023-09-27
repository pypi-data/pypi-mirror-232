from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    detail: str = Field(default="OK", example="OK")
