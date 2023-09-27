from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from examuploader import __version__
from examuploader.api import router

app = FastAPI(
    title="Web application to upload exam files to by SaveDownloadExam!",
    openapi_url="/doc/openapi.json",
    docs_url="/doc/docs",
    redoc_url="/doc/redoc",
    version=__version__,
)


app.include_router(router)


description = """---

## Contact
"""

tag_metadata = [
    {"name": "Upload File", "description": "Upload the exam file"},
    {"name": "Health", "description": "Check if the api is still running."},
]
openapi_schema = get_openapi(
    title="Web application to upload exam files to by SaveDownloadExam!",
    description=description,
    contact={
        "name": "Sebastian Stigler",
        "url": "https://image.informatik.htw-aalen.de/~stigler",
        "email": "sebastian.stigler@hs-aalen.de",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    tags=tag_metadata,
    version=__version__,
    routes=app.routes,
)

app.openapi_schema = openapi_schema