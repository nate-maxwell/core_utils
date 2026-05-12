from functools import wraps
from typing import Any
from typing import Callable
from typing import Optional



class DomainError(Exception):
    """
    Raised when a decorated operation fails.

    Carries a status code and comment that the transport layer can translate
    into whatever protocol-specific error response is appropriate.

    Args:
        status_code (int): Numeric code categorizing the failure.
        detail (str): Human-readable description of the failure.
    """
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def raises_domain_error(
        status_code: int = 400,
        comment: Optional[str] = None
    ) -> Callable[..., Any]:
    """
    Wrap a function so any exception is re-raised as a DomainError.

    Args:
        status_code (int): Status code to attach to the raised DomainError.
        comment (Optional[str]): Override message. If None, the original
            exception's string is used.
    Returns:
        Callable: A decorator that converts exceptions into DomainError.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except DomainError:
                raise
            except Exception as e:
                detail = str(e) if comment is None else comment
                raise DomainError(status_code=status_code, detail=detail) from e

        wrapper.status_code = status_code
        wrapper.comment = comment
        return wrapper

    return decorator
