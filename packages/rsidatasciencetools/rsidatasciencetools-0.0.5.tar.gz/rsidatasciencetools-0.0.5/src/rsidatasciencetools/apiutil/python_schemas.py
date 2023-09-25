from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Dict, Tuple
from pandas import Timestamp

class Ping(BaseModel):
    isThere: bool

class ApiInput(BaseModel):
    Name: str

class ApiOutput(BaseModel):
    Response: str    

