from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Beryl MVP API", version="1.0.0")

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(payload: RegisterIn):
    return {"email": payload.email, "status": "success"}

app.include_router(router, prefix="/users", tags=["users"])

@app.get("/")
def root():
    return {"message": "API Beryl_MVP opérationnelle"}
