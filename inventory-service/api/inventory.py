import os
from fastapi import APIRouter, Depends, HTTPException, Request, status

from database import get_db
from schemas.inventory import InventoryResponse, InventoryPayload
from sqlalchemy.orm import Session
from models.inventory import CreateInventory
import httpx  # pyright: ignore[reportMissingImports]

router = APIRouter()

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=InventoryResponse,
    description="Submit inventory data",
)
async def submit_inventory(
    request: Request, inventory_payload: InventoryPayload, db: Session = Depends(get_db)
):
    try:
        response = await fetchCategories(request, inventory_payload.category)

        category_name = response.get("name")
        print(category_name)
        if not category_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category name not found in response: {response}",
            )
        db_item = CreateInventory(
            product_name=inventory_payload.product_name,
            category=category_name,
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


async def fetchCategories(request, categoryId):
    async with httpx.AsyncClient() as client:
        token = request.cookies.get("access_token")
        try:
            cookies = {"access_token": token}
            url = f"{PRODUCT_SERVICE_URL}/categories/{categoryId}"
            response = await client.get(
                url, cookies=cookies, timeout=10.0, follow_redirects=True
            )
            response.raise_for_status()  # raise error if not 200
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Product service error: {e.response.text}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching categories: {str(e)}",
            )
