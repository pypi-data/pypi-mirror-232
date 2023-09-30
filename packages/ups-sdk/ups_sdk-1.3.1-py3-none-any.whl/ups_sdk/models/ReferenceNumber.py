from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
class ReferenceNumber(BaseModel):
    Code: str
    Value: Optional[str]