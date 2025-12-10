from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from database import get_db
from fastapi import Depends, HTTPException, status
from services.search_service import SearchService
from typing import Any, List, Optional
router = APIRouter()

@router.get("/",status_code=status.HTTP_200_OK,summary="Search across multiple indices (movies, theaters, showings, bookings)",response_model=Any)
def search_booking(
    query: str,
    indices: Optional[List[str]] = Query(
        None,
        description="Optional list of indices to search. Available: movies, theaters, showings, bookings. If not provided, searches all indices."
    ),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search across multiple Elasticsearch indices.
    
    - **query**: Search query string
    - **indices**: Optional comma-separated list of indices to search (e.g., "movies,theaters")
    
    Returns results from all specified indices with metadata including:
    - _index: The index name (e.g., "movies", "theaters")
    - _id: Document ID
    - _score: Relevance score
    - All original document fields
    """
    try:
        search_service = SearchService(db)
        search_results = search_service.search_booking(query, indices=indices)
        return {
            "query": query,
            "indices_searched": indices if indices else ["movies", "theaters", "showings", "bookings"],
            "total_results": len(search_results),
            "results": search_results
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error searching: {e}")