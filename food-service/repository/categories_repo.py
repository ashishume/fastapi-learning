from models.categories import Category
from schemas.categories import CategoryCreate
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
import uuid
import json
from datetime import datetime
from core.redis_client import get_sync_redis_client
import logging

logger = logging.getLogger(__name__)

class CategoryRepository:
    def __init__(self,db:Session):
        self.db=db

    def create_category(self,category:CategoryCreate) -> Category:
        new_category = Category(name=category.name, slug=category.slug, description=category.description)
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        # Invalidate cache after creating new category
        self._invalidate_category_cache(new_category.id)
        return new_category
    
    def get_all_categories(self) -> List[Category]:
        return self.db.execute(select(Category).order_by(Category.created_at.desc())).scalars().all()

    def get_category_by_id(self,category_id:uuid.UUID) -> Optional[Category]:
        # Check if category exists in Redis cache
        try:
            redis_client = get_sync_redis_client()
            if redis_client:
                cache_key = f"category:{category_id}"
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    # Deserialize from JSON
                    category_dict = json.loads(cached_data)
                    # Convert UUID string back to UUID object
                    category_dict['id'] = uuid.UUID(category_dict['id'])
                    # Convert datetime strings back to datetime objects
                    category_dict['created_at'] = datetime.fromisoformat(category_dict['created_at'])
                    category_dict['updated_at'] = datetime.fromisoformat(category_dict['updated_at'])
                    # Create Category object from dict
                    category = Category(**category_dict)
                    logger.debug(f"Cache hit for category {category_id}")
                    return category
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}. Falling back to database.")
        
        # If not in cache, get from database
        category = self.db.execute(select(Category).filter(Category.id == category_id)).scalar_one_or_none()
        
        # If category found, cache it in Redis
        if category:
            try:
                redis_client = get_sync_redis_client()
                if redis_client:
                    cache_key = f"category:{category_id}"
                    # Serialize to JSON (convert datetime to ISO format strings)
                    category_dict = {
                        'id': str(category.id),
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description,
                        'created_at': category.created_at.isoformat(),
                        'updated_at': category.updated_at.isoformat()
                    }
                    # Cache for 1 hour (3600 seconds)
                    redis_client.setex(cache_key, 3600, json.dumps(category_dict))
                    logger.debug(f"Cached category {category_id}")
            except Exception as e:
                logger.warning(f"Redis cache write error: {e}")
        
        return category
    
    def _invalidate_category_cache(self, category_id: uuid.UUID):
        """Invalidate cache for a specific category"""
        try:
            redis_client = get_sync_redis_client()
            if redis_client:
                cache_key = f"category:{category_id}"
                redis_client.delete(cache_key)
                logger.debug(f"Invalidated cache for category {category_id}")
        except Exception as e:
            logger.warning(f"Redis cache invalidation error: {e}")