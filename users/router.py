from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from uuid import uuid4

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    phone: str | None = None

@router.post("/register")
def register(payload: RegisterIn):
    # Stub de création: on renvoie un ID factice pour valider le flux
    return {
        "user_id": str(uuid4()),
        "email": payload.email,
        "status": "created"
    }
