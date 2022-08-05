import inspect
from typing import Any, Optional, Dict

from fastapi import HTTPException


class APIHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code, [{"msg": detail, "type": inspect.stack()[1].function}], headers
        )
