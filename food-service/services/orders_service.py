from repository.orders_repo import OrdersRepository
from schemas.orders import OrderAddFoodResponse, OrderCreate, OrderResponse
from models.orders import Order
from typing import List
import uuid
from sqlalchemy.orm import Session
class OrdersService:
    def __init__(self,db:Session):
        self.orders_repository = OrdersRepository(db)

    def create_order(self,order:OrderCreate,user_id:uuid.UUID) -> OrderResponse:
        return self.orders_repository.create_order(order=order,user_id=user_id)

    def get_all_orders(self) -> List[OrderResponse]:
        return self.orders_repository.get_all_orders()

    def get_order_by_id(self,order_id:uuid.UUID) -> OrderResponse:
        return self.orders_repository.get_order_by_id(order_id)

    def add_food_to_order(self,order:OrderCreate,new_order_id:uuid.UUID) -> OrderAddFoodResponse:
        return self.orders_repository.add_food_to_order(order=order,new_order_id=new_order_id)