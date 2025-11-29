from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from schemas.orders import OrderAddFoodResponse, OrderCreate, OrderResponse
from models.orders import Order, OrderStatus
from models.food_orders import FoodOrder
from models.menu import Menu
from typing import List
import uuid
class OrdersRepository:
    def __init__(self,db:Session):
        self.db = db

    def create_order(self,order:OrderCreate,user_id:uuid.UUID) -> OrderResponse:
        total_price = 0
        for menu_id in order.menu_ids:
            menu = self.db.execute(select(Menu).where(Menu.id == menu_id)).scalar_one_or_none()
            if menu is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
            total_price += menu.price

        new_order = Order(
            user_id=user_id,
            order_number=str(uuid.uuid4()).replace("-", "")[:8].upper(),
            total_price=total_price,
            status=OrderStatus.CONFIRMED,
        )
        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)
        return new_order

    def get_all_orders(self) -> List[OrderResponse]:
        return self.db.execute(select(Order).options(joinedload(Order.food_orders).joinedload(FoodOrder.menus))).unique().scalars().all()

    def get_order_by_id(self,order_id:uuid.UUID) -> OrderResponse:
        return self.db.execute(select(Order).options(joinedload(Order.food_orders).joinedload(FoodOrder.menus)).where(Order.id == order_id)).scalar_one_or_none()

    def add_food_to_order(self,order:OrderCreate,new_order_id:uuid.UUID) -> uuid.UUID:

        try:
            for menu_id in order.menu_ids:
                food_order = FoodOrder(
                    order_id=new_order_id,
                    menu_id=menu_id,
                    quantity=order.quantity,
                )
                self.db.add(food_order)
            self.db.commit()
            return new_order_id
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Database error: {e}")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error adding food to order: {e}")