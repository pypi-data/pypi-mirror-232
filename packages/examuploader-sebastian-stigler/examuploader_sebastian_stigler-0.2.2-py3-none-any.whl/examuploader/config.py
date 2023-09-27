import os
from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings_yaml import YamlBaseSettings
from pydantic_settings import SettingsConfigDict


class Course(BaseModel):
    name: str = Field(
        description="Name of the course / directory to store the uploads for this course",
        example="python101",
    )
    students: List[str] = Field(
        description="List of student in the course, use trailing asterisk for globbing",
        example=["heinz", "python101-*"],
    )


class Settings(YamlBaseSettings):

    upload_path: str = Field(description="Base path to upload files to")
    courses: List[Course]

    model_config = SettingsConfigDict(
        secrets_dir=os.environ.get("EXAM_UPLOADER_SECRETS_DIR", "/tmp/secrets"),
        yaml_file=os.environ.get("EXAM_UPLOADER_CONFIG", "config.yaml")
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
