from sqlalchemy.orm import Session
from typing import List
from models.bookings import Booking
from models.movies import Movie
from models.theaters import Theater
from core.elasticsearch_client import get_elasticsearch_client
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_booking(self, query: str, indices: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search across multiple Elasticsearch indices.
        
        Args:
            query: Search query string
            indices: Optional list of indices to search. If None, searches all indices.
                    Available indices: "movies", "theaters", "showings", "bookings"
        
        Returns:
            List of search results with metadata about source index and type
        """
        es_client = get_elasticsearch_client()
        
        # Default to searching all indices if not specified
        if indices is None:
            indices = ["movies", "theaters", "showings", "bookings"]
        
        # Define searchable fields for each index type
        # Using multi_match with all text fields across indices
        searchable_fields = [
            # Movies fields
            "title^3", "description^2", "genre^2", "director", "cast",
            # Theaters fields
            "name^3", "description^2", "location^2", "address", "city^2",
            # Showings fields (limited text fields)
            # Bookings fields
            "booking_number^2"
        ]
        
        # Elasticsearch 8.x API: query parameter instead of body
        response = es_client.search(
            index=indices,
            query={
                "multi_match": {
                    "query": query,
                    "fields": searchable_fields,
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                    "operator": "or"
                }
            },
            # Include index name in response for result identification
            source=True
        )
        
        # Format results with index type information
        results = []
        for hit in response["hits"]["hits"]:
            result = hit["_source"].copy()
            result["_index"] = hit["_index"]  # Add index name to identify result type
            result["_id"] = hit["_id"]  # Add document ID
            result["_score"] = hit["_score"]  # Add relevance score
            results.append(result)
        
        return results

    def sync_movie_to_elasticsearch(self, movie: Movie) -> bool:
        """
        Sync a single movie from database to Elasticsearch.
        
        Args:
            movie: Movie model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            es_client = get_elasticsearch_client()
            
            # Convert movie to dictionary, handling UUID and datetime serialization
            movie_doc = {
                "id": str(movie.id),
                "title": movie.title,
                "description": movie.description,
                "duration_minutes": movie.duration_minutes,
                "genre": movie.genre,
                "director": movie.director,
                "release_date": movie.release_date.isoformat() if movie.release_date else None,
                "rating": movie.rating,
                "language": movie.language,
                "is_imax": movie.is_imax,
                "poster_url": movie.poster_url,
                "trailer_url": movie.trailer_url,
                "cast": movie.cast if movie.cast else [],
                "created_at": movie.created_at.isoformat() if movie.created_at else None,
                "updated_at": movie.updated_at.isoformat() if movie.updated_at else None,
            }
            
            # Index the movie document (creates or updates)
            es_client.index(
                index="movies",
                id=str(movie.id),
                document=movie_doc
            )
            logger.info(f"Synced movie {movie.id} to Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Error syncing movie {movie.id} to Elasticsearch: {str(e)}")
            return False

    def sync_all_movies_to_elasticsearch(self) -> int:
        """
        Sync all movies from database to Elasticsearch.
        
        Returns:
            int: Number of movies successfully synced
        """
        try:
            movies = self.db.query(Movie).all()
            synced_count = 0
            
            for movie in movies:
                if self.sync_movie_to_elasticsearch(movie):
                    synced_count += 1
            
            logger.info(f"Synced {synced_count}/{len(movies)} movies to Elasticsearch")
            return synced_count
        except Exception as e:
            logger.error(f"Error syncing all movies to Elasticsearch: {str(e)}")
            return 0

    def delete_movie_from_elasticsearch(self, movie_id: str) -> bool:
        """
        Delete a movie from Elasticsearch.
        
        Args:
            movie_id: Movie ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            es_client = get_elasticsearch_client()
            es_client.delete(index="movies", id=movie_id)
            logger.info(f"Deleted movie {movie_id} from Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Error deleting movie {movie_id} from Elasticsearch: {str(e)}")
            return False

    def sync_theatre_with_elastic_search(self, theatre: Theater) -> bool:
        """
        Sync a single theater from database to Elasticsearch.
        
        Args:
            theatre: Theater model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            es_client = get_elasticsearch_client()
            
            # Convert theater to dictionary, handling UUID and datetime serialization
            theatre_doc = {
                "id": str(theatre.id),
                "name": theatre.name,
                "description": theatre.description,
                "location": theatre.location,
                "address": theatre.address,
                "city": theatre.city,
                "created_at": theatre.created_at.isoformat() if theatre.created_at else None,
                "updated_at": theatre.updated_at.isoformat() if theatre.updated_at else None,
            }
            
            # Index the theater document (creates or updates)
            es_client.index(
                index="theaters",
                id=str(theatre.id),
                document=theatre_doc
            )
            logger.info(f"Synced theater {theatre.id} to Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Error syncing theater {theatre.id} to Elasticsearch: {str(e)}")
            return False    
