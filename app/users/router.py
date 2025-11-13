from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    phone: str | None = None

@router.post("/register")
def register(payload: RegisterIn):
    return {"id": "demo", "email": payload.email}
