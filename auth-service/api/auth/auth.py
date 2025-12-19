import logging
from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session


from core.database import get_db
from core.utils import auth_guard, create_access_token, hash_password, verify_password, verify_token
from models.user import User
from schemas.user import LoginPayload, LoginResponse, RequestPayload, ResponseModel, UserDetailResponse


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
        )

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return ResponseModel(id=db_item.id, email=db_item.email, name=db_item.name)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed {e}"
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    req_payload: LoginPayload, response: Response, db: Session = Depends(get_db)
) -> dict[str,str]:
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

        access_token = create_access_token(data={"auth_user": existing_user.email,"auth_user_id": str(existing_user.id)})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30, # 30 days
        )

        return {
            "message": "Login success",
            "email": existing_user.email,
            "id": str(existing_user.id),
            "name": existing_user.name,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed {e}"
        )


@router.get("/user_details", response_model=UserDetailResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(auth_guard)])
def get_user_details(request:Request, db: Session = Depends(get_db)) -> UserDetailResponse:
    try:
        user_id = str(request.state.user_id)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
        return UserDetailResponse(id=user.id, email=user.email, name=user.name)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed {e}")

@router.post("/logout")
def logout(response: Response):
    try:
        response.delete_cookie("access_token")
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed {e}")
