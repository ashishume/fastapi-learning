import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from core.database import get_db
from models.category import Category
from schemas.category import CategoryCreate, CategoryResponse, CategoryResponseList
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def category_create(
    item: CategoryCreate, db: Session = Depends(get_db)
) -> CategoryResponse:
    try:
        logger.info(f"Category created ${item.name}")
        db_item = Category(name=item.name, slug=item.slug, description=item.description)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        logger.info("successfully added")
        return db_item

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error while creating item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"db error ${str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="db error"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"unexpected error {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unexpected error"
        )


@router.get("/", response_model=CategoryResponseList, status_code=status.HTTP_200_OK)
def read_categories(db: Session = Depends(get_db)):
    try:
        logger.info("fetching categories")
        db_item = db.query(Category).all()
        return {"categories": db_item}
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error"
        )


@router.get(
    "/{categoryId}", response_model=CategoryResponse, status_code=status.HTTP_200_OK
)
def fetch_by_category_id(
    categoryId: str, db: Session = Depends(get_db)
) -> CategoryResponse:
    try:
        logger.info("fetching category by id")
        db_item = db.query(Category).filter(Category.id == categoryId).first()

        if not db_item:
            raise HTTPException(
                detail="category id not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return db_item
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error"
        )
