from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db
from models.item import Item
from schemas.item import ItemCreate, ItemListResponse, ItemResponse
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    try:
        db_item = Item(name=item.name, description=item.description)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error:{str(e)}")


@router.get("/", response_model=ItemListResponse)
def read_item(db: Session = Depends(get_db)):
    item_list = db.query(Item).all()
    return {"products": item_list}
