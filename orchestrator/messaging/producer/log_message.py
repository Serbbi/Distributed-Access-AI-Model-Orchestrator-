from pydantic import BaseModel, UUID4

# status enum
from enum import Enum

class Status(str, Enum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    TIMEOUT = 'TIMEOUT'
    RUNNING = 'RUNNING'

class MetaData(BaseModel):
    id: UUID4
    # code: str
    start: int
    end: int
    duration: int
    status: Status
    exitCode: int = None

class LogMessage(BaseModel):
    id: UUID4
    content: str
    metadata: MetaData
