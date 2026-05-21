from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from api.v1.router import api_router
from core.exceptions import DatabaseOperationError, UserUnauthorizedError, ResourceCreationError
from utils.logger import log_database_operation_error, log_unauthorized_user

app = FastAPI(title="Fokusin RESTful API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Fokusin RESTful API. Please use /docs for API documentation."}

@app.exception_handler(DatabaseOperationError)
async def database_operation_error_handler(request: Request, exc: DatabaseOperationError):
    """
    Handle DatabaseOperationError exception into HTTP 500 response.
    """
    if exc.__cause__:
        log_database_operation_error(exc.__cause__)
    else:
        log_database_operation_error()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Terjadi kesalahan pada sistem. Silahkan coba lagi nanti."
        }
    )

@app.exception_handler(ResourceCreationError)
async def resource_creation_error_handler(request: Request, exc: ResourceCreationError):
    """
    Handle ResourceCreationError exception into HTTP 400 response.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message
        }
    )

@app.exception_handler(UserUnauthorizedError)
async def user_unauthorized_error_handler(request: Request, exc: UserUnauthorizedError):
    """
    Handle UserUnauthorizedError exception into HTTP 401 response.
    """
    log_unauthorized_user(exc.user_id)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Anda tidak memiliki akses untuk melakukan operasi ini."
        }
    )
