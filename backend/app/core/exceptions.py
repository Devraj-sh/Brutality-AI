from fastapi import HTTPException, status

class BrutalityException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class EntityNotFoundException(BrutalityException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            detail=f"{entity_name} with id '{entity_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

class UnauthorizedException(BrutalityException):
    def __init__(self, detail: str = "Invalid credentials or token expired."):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class ForbiddenException(BrutalityException):
    def __init__(self, detail: str = "Permission denied."):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )
