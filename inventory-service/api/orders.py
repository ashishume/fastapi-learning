import os
from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, Request,status
from sqlalchemy.exc import SQLAlchemyError
from schemas.orders import OrderCreate, OrderResponse, OrderDetailResponse
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.orders import Order
import httpx  # pyright: ignore[reportMissingImports]
router= APIRouter()


@router.post('/',response_model=OrderResponse,status_code=status.HTTP_201_CREATED)
def create_order(order_payload:OrderCreate,request:Request,db:Session=Depends(get_db)) -> OrderResponse:
    try:
        db_item=Order(
            user_id=request.state.user_id,
            product_id=order_payload.product_id,
            quantity=order_payload.quantity,
            total_price=order_payload.total_price,
            status=order_payload.status,
            created_at=order_payload.created_at,
            updated_at=order_payload.updated_at,
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Integrity error: {e}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Database error: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Unexpected error: {e}")



@router.get('/',response_model=list[OrderResponse],status_code=status.HTTP_200_OK)
def get_orders(db:Session=Depends(get_db)) -> dict[str, list[OrderResponse]]:
    try:
        db_items=db.query(Order).all()
        return {"orders": db_items}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Unexpected error: {e}")

@router.get('/{order_id}',response_model=OrderDetailResponse,status_code=status.HTTP_200_OK)
async def get_order(order_id:int,request:Request,db:Session=Depends(get_db)) -> OrderDetailResponse:
    try:
        db_item=db.query(Order).filter(Order.id == order_id).first()
        print("user_id",request.state.user_id)
        print("db_item",db_item)
        if not db_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Order with id {order_id} not found")

        product = await fetch_product(db_item.product_id,request)
        return {"order": db_item, "product": product}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Database error: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Unexpected error: {e}")




PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")
async def fetch_product(product_id:int,request:Request):
    try:
        async with httpx.AsyncClient() as client:
            token = request.cookies.get("access_token")
            cookies = {"access_token": token}
            url = f"{PRODUCT_SERVICE_URL}/items/{product_id}"
            response = await client.get(url, cookies=cookies, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            product = response.json()
            return product
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code,detail=f"Product service error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Unexpected error: {e}")
