import logging
import os.path
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends, Header
from pydantic import ValidationError

from examuploader.config import Settings, get_settings
from examuploader.models.upload_data import UploadData
from examuploader.models.generic_response import GenericResponse
from examuploader.models.http_error import HTTPError

router = APIRouter(tags=["Upload File"])
logger = logging.getLogger("uvicorn.error")

@router.post(
    "/upload",
    responses={
        status.HTTP_200_OK: {"model": GenericResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPError},
    },
)
async def upload(
    x_course: Annotated[str, Header()],
    x_student: Annotated[str, Header()],
    x_exam_type: Annotated[str, Header()],
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    try:
        data = UploadData(course=x_course, student=x_student, exam_type=x_exam_type)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=str(err))

    # check if data.course exist in settings:
    try:
        course = next(
            filter(lambda entry: entry.name == data.course, settings.courses)
        )
    except StopIteration:
        raise HTTPException(
            status_code=403, detail=f"Course '{data.course}' doesn't exist."
        )

    # check if student is in the course
    for enrolled_student in course.students:
        if enrolled_student == data.student:
            break
        if enrolled_student.endswith("*") and data.student.startswith(
            enrolled_student[:-1]
        ):
            break
    else:
        raise HTTPException(
            status_code=403,
            detail=f"Student '{data.student}' is not enrolled in '{course.name}'.",
        )
    # check if upload_path exists
    if not os.path.isdir(settings.upload_path):
        raise HTTPException(
            status_code=403,
            detail=f"The upload_path '{settings.upload_path}' doesn't exist!",
        )
    # create course in upload_path
    upload_path = os.path.join(settings.upload_path, course.name)
    if not os.path.isdir(upload_path):
        try:
            os.makedirs(upload_path, mode=0o770, exist_ok=True)
        except Exception:
            raise HTTPException(
                status_code=403,
                detail=f"The course '{course.name}' couldn't be created in the upload_path '{settings.upload_path}'.",
            )

    try:
        contents = file.file.read()
        filename_s = file.filename.split('.')
        suffix = filename_s.pop()
        filename = f"{data.exam_type}_{'.'.join(filename_s)}_{datetime.now().strftime('%Y%m%dT%H%M%Sx%f')}.{suffix}"
        with open(os.path.join(upload_path, filename), "wb") as f:
            f.write(contents)
        logger.info(f"Upload of {filename} from {data.course}/{data.student} was successful.")
    except Exception:
        raise HTTPException(
            status_code=403, detail="Couldn't save file {file.filename}"
        )
    finally:
        file.file.close()

    return GenericResponse(detail="Fileupload successful.")
