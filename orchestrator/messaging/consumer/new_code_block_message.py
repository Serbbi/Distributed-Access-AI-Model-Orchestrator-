# use pydantic
from pydantic import BaseModel, UUID4

class NewCodeBlockMessage(BaseModel):
    id: UUID4
    code: str
    cassandra_pod_ip: str