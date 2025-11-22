from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    retcode: int
    message: str
    data: Optional[Any] = None