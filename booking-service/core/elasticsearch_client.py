"""Elasticsearch client configuration and utilities."""

import os
import logging
from typing import Optional
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get Elasticsearch configuration from environment variables
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}")

# Global Elasticsearch client instance
es_client: Optional[Elasticsearch] = None


def get_elasticsearch_client() -> Elasticsearch:
    """
    Get or create Elasticsearch client instance.
    
    Returns:
        Elasticsearch: Elasticsearch client instance
    """
    global es_client
    
    if es_client is None:
        try:
            es_client = Elasticsearch(
                [ELASTICSEARCH_URL],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True,
            )
            # Test connection
            if es_client.ping():
                logger.info(f"Successfully connected to Elasticsearch at {ELASTICSEARCH_URL}")
            else:
                logger.warning(f"Elasticsearch ping failed at {ELASTICSEARCH_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
            raise
    
    return es_client


def close_elasticsearch_client():
    """
    Close Elasticsearch client connection.
    """
    global es_client
    
    if es_client is not None:
        try:
            es_client.close()
            logger.info("Elasticsearch client connection closed")
        except Exception as e:
            logger.error(f"Error closing Elasticsearch client: {str(e)}")
        finally:
            es_client = None


def create_index_if_not_exists(index_name: str, mapping: Optional[dict] = None):
    """
    Create an Elasticsearch index if it doesn't exist.
    
    Args:
        index_name: Name of the index to create
        mapping: Optional index mapping configuration
    """
    try:
        client = get_elasticsearch_client()
        
        if not client.indices.exists(index=index_name):
            # Elasticsearch 8.x API: pass mappings directly, not in body
            index_config = {}
            if mapping:
                index_config["mappings"] = mapping
            
            client.indices.create(index=index_name, **index_config)
            logger.info(f"Created Elasticsearch index: {index_name}")
        else:
            logger.info(f"Elasticsearch index already exists: {index_name}")
    except Exception as e:
        logger.error(f"Error creating Elasticsearch index {index_name}: {str(e)}")
        raise

