from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from schemas.inventory import InventoryResponse, InventoryPayload
from sqlalchemy.orm import Session
from models.inventory import CreateInventory

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=InventoryResponse,
    description="Submit inventory data",
)
def submit_inventory(
    inventory_payload: InventoryPayload, db: Session = Depends(get_db)
):
    try:
        db_item = CreateInventory(
            product_name=inventory_payload.product_name,
            category=inventory_payload.category,
            quantity_in_stock=inventory_payload.quantity_in_stock,
            unit_price=inventory_payload.unit_price,
            last_restock_date=inventory_payload.last_restock_date,
            supplier=inventory_payload.supplier,
            reorder_point=inventory_payload.reorder_point,
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        return db_item
    except Exception as e:
        raise HTTPException(
            detail=f"error {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[InventoryResponse])
def get_data(db: Session = Depends(get_db)):
    try:
        inventory_items = db.query(CreateInventory).all()
        return inventory_items
    except Exception as e:
        raise HTTPException(
            detail=f"error {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
