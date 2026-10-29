"""Application-specific custom exceptions."""


class AppError(Exception):
    """Base class for application errors with a safe client-facing message."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class EmployeeNotFoundError(NotFoundError):
    """Raised when an employee does not exist."""

    def __init__(self, message: str = "Employee not found") -> None:
        super().__init__(message)


class ProjectNotFoundError(NotFoundError):
    """Raised when a project does not exist."""

    def __init__(self, message: str = "Project not found") -> None:
        super().__init__(message)


class UserNotFoundError(NotFoundError):
    """Raised when a user does not exist."""

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)


class ConflictError(AppError):
    """Raised when a request conflicts with current application state."""

    def __init__(
        self,
        message: str = "The request conflicts with current state",
    ) -> None:
        super().__init__(message)


class EmployeeAlreadyAssignedError(ConflictError):
    """Raised when an employee is already assigned to a project."""

    def __init__(
        self,
        message: str = "Employee is already assigned to one of these projects",
    ) -> None:
        super().__init__(message)


class DatabaseError(AppError):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "A database error occurred") -> None:
        super().__init__(message)


class InvalidCredentialsError(AppError):
    """Raised when a login identifier or password is invalid."""

    def __init__(
        self,
        message: str = "Invalid username/email or password",
    ) -> None:
        super().__init__(message)


class ForbiddenError(AppError):
    """Raised when an authenticated user lacks required permissions."""

    def __init__(
        self,
        message: str = "You do not have permission to access this resource",
    ) -> None:
        super().__init__(message)


class JWTConfigurationError(Exception):
    """Raised when JWT configuration is missing or invalid."""

    def __init__(
        self,
        message: str = "JWT configuration is invalid",
    ) -> None:
        super().__init__(message)


class InvalidAccessTokenError(Exception):
    """Raised when an access token is invalid, expired, or malformed."""

    def __init__(
        self,
        message: str = "The access token is invalid or expired",
    ) -> None:
        super().__init__(message)


class DuplicateUserError(ConflictError):
    """Raised when attempting to create a user that already exists."""

    def __init__(
        self,
        message: str = "A user with this username or email already exists",
    ) -> None:
        super().__init__(message)
