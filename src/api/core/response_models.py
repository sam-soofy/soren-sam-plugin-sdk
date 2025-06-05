from typing import Optional, Any
from pydantic import BaseModel


class StandardResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Any] = None
