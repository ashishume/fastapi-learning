"""Elasticsearch index mappings and configurations."""

from typing import Dict, Any, List

# Define all Elasticsearch index mappings
ELASTICSEARCH_INDICES: Dict[str, Dict[str, Any]] = {
    "movies": {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "description": {"type": "text", "analyzer": "standard"},
                "duration_minutes": {"type": "integer"},
                "genre": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "director": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "release_date": {"type": "date"},
                "rating": {"type": "float"},
                "language": {"type": "keyword"},
                "is_imax": {"type": "boolean"},
                "poster_url": {"type": "keyword"},
                "trailer_url": {"type": "keyword"},
                "cast": {"type": "text", "analyzer": "standard"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
    },
    "theaters": {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "description": {"type": "text", "analyzer": "standard"},
                "location": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "address": {"type": "text", "analyzer": "standard"},
                "city": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
    },
    "showings": {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "movie_id": {"type": "keyword"},
                "theater_id": {"type": "keyword"},
                "show_start_datetime": {"type": "date"},
                "show_end_datetime": {"type": "date"},
                "available_seats": {"type": "integer"},
                "is_active": {"type": "boolean"},
                "expires_at": {"type": "date"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
    },
    "bookings": {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "showing_id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "booking_number": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "total_price": {"type": "float"},
                "status": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
    }
}


def get_index_mapping(index_name: str) -> Dict[str, Any]:
    """
    Get the mapping configuration for a specific index.
    
    Args:
        index_name: Name of the index
        
    Returns:
        Dict containing the index mapping configuration
        
    Raises:
        ValueError: If the index name is not found
    """
    if index_name not in ELASTICSEARCH_INDICES:
        raise ValueError(f"Index '{index_name}' not found in ELASTICSEARCH_INDICES")
    
    return ELASTICSEARCH_INDICES[index_name]["mappings"]


def get_all_index_names() -> List[str]:
    """
    Get a list of all defined index names.
    
    Returns:
        List of index names
    """
    return list(ELASTICSEARCH_INDICES.keys())

