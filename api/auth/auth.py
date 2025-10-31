import logging
from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from core.database import get_db
from core.utils import hash_password, verify_password
from models.user import User
from schemas.user import LoginPayload, LoginResponse, RequestPayload, ResponseModel


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
def signup(req_payload: RequestPayload, db: Session = Depends(get_db)) -> ResponseModel:
    try:
        existing_user = db.query(User).filter(User.email == req_payload.email).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered",
            )
        hashed_pass = hash_password(req_payload.password)
        db_item = User(
            email=req_payload.email,
            name=req_payload.name,
            hashed_password=hashed_pass,
            token=req_payload.token,
        )

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return {"id": db_item.id, "email": db_item.email, "name": db_item.name}
    except HTTPException:
        # Re-raise HTTPExceptions (like "User already registered")
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed {e}"
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(req_payload: LoginPayload, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        existing_user = db.query(User).filter(User.email == req_payload.email).first()

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login credentials incorrect",
            )

        pass_correct = verify_password(
            req_payload.password, existing_user.hashed_password
        )

        if not pass_correct:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login credentials incorrect",
            )

        return {"message": "Login success", "email": existing_user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed {e}"
        )
