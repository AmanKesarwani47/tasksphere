from fastapi import APIRouter, status, Depends, HTTPException, status
from app.schemas.users import CurrentUserResponse, UserResponse, UserCreate
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users", "Me"])

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter((User.email == payload.email) | (User.username == payload.user_name)).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered.",
        )

    secure_password = hash_password(payload.password)

    new_user = User(
        username=payload.user_name,
        email=payload.email,
        hashed_password=secure_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=list[UserResponse])
def list_user(db: Session = Depends(get_db)):
    return db.query(User).all()
    