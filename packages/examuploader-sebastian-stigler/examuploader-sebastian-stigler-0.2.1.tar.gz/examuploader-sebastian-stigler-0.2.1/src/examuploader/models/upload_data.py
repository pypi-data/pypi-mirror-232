from enum import Enum

from pydantic import BaseModel, Field


class ExamType(str, Enum):
    Exam: str = "exam"
    TestExam: str = "testexam"


class UploadData(BaseModel):
    student: str = Field(description="Name of the jupyterhub user", example="heinz", pattern=r'^[a-zA-Z0-9-]+$')
    course: str = Field(description="Name of the course", example="python101", pattern=r'^[a-z0-9-]+$')
    exam_type: ExamType = Field(
        description="Type of the exam", example=ExamType.TestExam
    )
