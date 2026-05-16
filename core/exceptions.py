class DatabaseOperationError(Exception):
    """
    Raised when a database operation fails.
    """
    pass

class UserUnauthorizedError(Exception):
    """
    Raised when an operation is performed by an unauthorized user.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User {self.user_id} is not authorized to perform this operation.")