from core.logger import logger

def log_unauthorized_user(user_id: str):
    """
    Log that a user is not authorized to perform an operation.
    """
    logger.warning(f"User {user_id or ''} is not authorized to perform this operation.")

def log_database_operation_error(cause):
    """
    Log a database operation error.
    """
    logger.exception(f"Database Operation Error: {cause or 'Unknown cause'}")