from pydantic import BaseModel

class ClientCreate(BaseModel):
    name: str
    phone: str


class MasterCreate(BaseModel):
    name: str


class RequestCreate(BaseModel):
    device_type: str
    model: str
    problem: str
    client_id: int


class StatusUpdate(BaseModel):
    status: str


class AssignMaster(BaseModel):
    master_id: int


class UserCreate(BaseModel):
    username: str
    password: str
    role: str