from fastapi import HTTPException, status


class InvalidLoginDataException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Invalid username or password',
    ) -> None:
        super().__init__(status_code, detail)


class UserExistException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'User already exist',
    ) -> None:
        super().__init__(status_code, detail)


class NotActiveUserException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = 'The user is not active',
    ) -> None:
        super().__init__(status_code, detail)


class CredentialsException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = 'Could not validate credentials',
        headers: dict[str, str] = {'WWW-Authenticate': 'Bearer'},
    ) -> None:
        super().__init__(status_code, detail, headers)


class AvatarException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Could not decode avatar',
    ) -> None:
        super().__init__(status_code, detail)


class DbException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Could not save these data'
    ) -> None:
        super().__init__(status_code, detail)
