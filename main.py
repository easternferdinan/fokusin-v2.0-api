from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from api.v1.router import api_router
from core.exceptions import DatabaseOperationError

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
    print(f"Database Operation Error: {exc.__cause__ or 'Unknown error'}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc)
        }
    )