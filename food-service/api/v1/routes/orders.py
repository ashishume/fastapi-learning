from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.orders import OrderCreate, OrderResponse
from database import get_db
from sqlalchemy.orm import Session
from services.orders_service import OrdersService
from models.food_orders import FoodOrder
from typing import List
import uuid
router=APIRouter()

@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new order",response_model=OrderResponse)
def create_order(order: OrderCreate,request:Request, db: Session = Depends(get_db)) -> OrderResponse:
    try:
        order_service = OrdersService(db)
        new_order = order_service.create_order(order=order,user_id=request.state.user_id)

        order_service.add_food_to_order(order=order,new_order_id=new_order.id)


        return OrderResponse.model_validate(new_order)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating order: {e}")


@router.get("/",status_code=status.HTTP_200_OK,summary="Get all orders",response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)) -> List[OrderResponse]:
    try:
        order_service = OrdersService(db)
        orders = order_service.get_all_orders()
        return [OrderResponse.model_validate(order) for order in orders]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting orders: {e}")
        
@router.get("/{order_id}",status_code=status.HTTP_200_OK,summary="Get an order by id",response_model=OrderResponse)
def get_order_by_id(order_id: uuid.UUID, db: Session = Depends(get_db)) -> OrderResponse:
    try:
        order_service = OrdersService(db)
        order = order_service.get_order_by_id(order_id)
        return OrderResponse.model_validate(order)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting order: {e}")