from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class ReferenceNumberItem(BaseModel):
    Code: str
    Value: Optional[str] = Field(None)