import datetime

from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    message: str = Field(
        description="Some arbitrary message", example="This is a healthcheck"
    )
    version: str = Field(description="Version", example="1.2.4")
    docs_url: str = Field(description="Url to Swagger documentation", example="/docs")
    redoc_url: str = Field(description="Url to Redocly documentation", example="/redoc")
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The current server time",
    )
