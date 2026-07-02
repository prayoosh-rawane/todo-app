from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import User
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user
from pydantic import BaseModel, Field
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

@router.get("/")
async def get_user(user: user_dependancy, db: db_dependancy):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    return user_model
# {
#         "id": 1,
#         "first_name": user_model.first_name,
#         "role": user_model.role,
#         "last_name": user_model.last_name,
#         "username": user_model.username,
#         "email": user_model.email,
#         "is_active": user_model.is_active
#     }

@router.put("/password")
async def change_password(user:user_dependancy, db:db_dependancy, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Verification Failed")
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/phonenumber", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependancy, db: db_dependancy, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()