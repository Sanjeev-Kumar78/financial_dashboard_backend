from fastapi import HTTPException

class AppException(HTTPException):
    # Base for all application-level errors.
    # Subclasses just supply a default status code and error code string.
    # The global handler in main.py ensures every error looks identical.
    def __init__(self, detail: str, status_code: int = 400, error_code: str = "APP_ERROR"):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404, error_code="NOT_FOUND")

class ForbiddenException(AppException):
    def __init__(self, detail: str = "You don't have permission to do this"):
        # 403 means authenticated but not authorized.
        # Use 401 only when the user is not authenticated at all.
        super().__init__(detail=detail, status_code=403, error_code="FORBIDDEN")

class BadRequestException(AppException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(detail=detail, status_code=400, error_code="BAD_REQUEST")

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail=detail, status_code=401, error_code="UNAUTHORIZED")
