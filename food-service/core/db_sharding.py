"""
Hash-based Database Sharding Implementation for Food Service.

This module provides a consistent hash-based sharding mechanism to distribute
data across multiple database shards. It uses a shard key (e.g., user_id, 
restaurant_id) to determine which shard should handle the data.

Usage:
    from core.db_sharding import ShardManager, get_sharded_db
    
    # Get session for a specific shard key
    shard_manager = ShardManager()
    db = shard_manager.get_session_for_key(user_id)
    
    # Or use the dependency injection
    def my_endpoint(db: Session = Depends(get_sharded_db(shard_key="user_id"))):
        ...
"""

import os
import hashlib
import logging
from typing import Generator, Dict, List, Optional, Any, Union
from functools import lru_cache
from contextlib import contextmanager

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ShardConfig:
    """Configuration for a single database shard."""
    
    def __init__(
        self,
        shard_id: int,
        host: str,
        port: str,
        database: str,
        user: str,
        password: str,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.shard_id = shard_id
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool_size = pool_size
        self.max_overflow = max_overflow
    
    @property
    def connection_url(self) -> str:
        """Generate the database connection URL."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
    
    def __repr__(self) -> str:
        return f"ShardConfig(id={self.shard_id}, host={self.host}, db={self.database})"


class ShardManager:
    """
    Manages multiple database shards with consistent hash-based routing.
    
    This class handles:
    - Creating and managing database engines for each shard
    - Hash-based shard key routing
    - Session management across shards
    - Health checking for shards
    
    The sharding uses consistent hashing based on a shard key (typically user_id
    or restaurant_id) to ensure data locality and even distribution.
    """
    
    _instance: Optional['ShardManager'] = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one ShardManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, shard_configs: Optional[List[ShardConfig]] = None):
        """
        Initialize the ShardManager with shard configurations.
        
        Args:
            shard_configs: Optional list of ShardConfig objects. If not provided,
                          configurations will be loaded from environment variables.
        """
        if self._initialized:
            return
            
        self._engines: Dict[int, Engine] = {}
        self._session_factories: Dict[int, sessionmaker] = {}
        self._shard_configs: Dict[int, ShardConfig] = {}
        
        # Load shard configurations
        configs = shard_configs or self._load_shard_configs_from_env()
        
        if not configs:
            logger.warning("No shard configurations found. Using default single database.")
            configs = [self._get_default_config()]
        
        for config in configs:
            self._register_shard(config)
        
        self._num_shards = len(configs)
        self._initialized = True
        logger.info(f"ShardManager initialized with {self._num_shards} shard(s)")
    
    def _load_shard_configs_from_env(self) -> List[ShardConfig]:
        """
        Load shard configurations from environment variables.
        
        Expected format:
            SHARD_COUNT=3
            SHARD_0_HOST=localhost
            SHARD_0_PORT=5437
            SHARD_0_DB=food_service_shard_0
            SHARD_0_USER=postgres
            SHARD_0_PASSWORD=admin
            ... (repeat for each shard)
        """
        configs = []
        shard_count = int(os.getenv("SHARD_COUNT", "0"))
        
        for i in range(shard_count):
            prefix = f"SHARD_{i}_"
            host = os.getenv(f"{prefix}HOST")
            
            if not host:
                logger.warning(f"Shard {i} configuration incomplete, skipping")
                continue
            
            config = ShardConfig(
                shard_id=i,
                host=host,
                port=os.getenv(f"{prefix}PORT", "5432"),
                database=os.getenv(f"{prefix}DB", f"food_service_shard_{i}"),
                user=os.getenv(f"{prefix}USER", "postgres"),
                password=os.getenv(f"{prefix}PASSWORD", "admin"),
                pool_size=int(os.getenv(f"{prefix}POOL_SIZE", "5")),
                max_overflow=int(os.getenv(f"{prefix}MAX_OVERFLOW", "10")),
            )
            configs.append(config)
        
        return configs
    
    def _get_default_config(self) -> ShardConfig:
        """Get default shard configuration from standard environment variables."""
        return ShardConfig(
            shard_id=0,
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5437"),
            database=os.getenv("POSTGRES_DB", "food_service"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "admin"),
        )
    
    def _register_shard(self, config: ShardConfig) -> None:
        """Register a new shard with its engine and session factory."""
        engine = create_engine(
            config.connection_url,
            pool_pre_ping=True,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
        )
        
        session_factory = sessionmaker(autoflush=False, bind=engine)
        
        self._engines[config.shard_id] = engine
        self._session_factories[config.shard_id] = session_factory
        self._shard_configs[config.shard_id] = config
        
        logger.info(f"Registered shard {config.shard_id}: {config}")
    
    def _hash_key(self, key: Union[str, uuid.UUID, int]) -> int:
        """
        Generate a consistent hash for the given key.
        
        Uses MD5 for consistent distribution across shards.
        
        Args:
            key: The shard key (user_id, restaurant_id, etc.)
            
        Returns:
            Integer hash value
        """
        if isinstance(key, uuid.UUID):
            key = str(key)
        elif isinstance(key, int):
            key = str(key)
        
        # Use MD5 for consistent hashing (good distribution, fast)
        hash_bytes = hashlib.md5(key.encode()).digest()
        # Convert first 8 bytes to integer
        hash_int = int.from_bytes(hash_bytes[:8], byteorder='big')
        return hash_int
    
    def get_shard_id(self, shard_key: Union[str, uuid.UUID, int]) -> int:
        """
        Determine which shard should handle the given key.
        
        Uses modulo operation on the hash to map to a shard ID.
        
        Args:
            shard_key: The key to route (e.g., user_id, restaurant_id)
            
        Returns:
            The shard ID (0-indexed)
        """
        hash_value = self._hash_key(shard_key)
        shard_id = hash_value % self._num_shards
        logger.debug(f"Key {shard_key} mapped to shard {shard_id}")
        return shard_id
    
    def get_engine(self, shard_id: int) -> Engine:
        """Get the SQLAlchemy engine for a specific shard."""
        if shard_id not in self._engines:
            raise ValueError(f"Shard {shard_id} not found. Available: {list(self._engines.keys())}")
        return self._engines[shard_id]
    
    def get_engine_for_key(self, shard_key: Union[str, uuid.UUID, int]) -> Engine:
        """Get the SQLAlchemy engine for a given shard key."""
        shard_id = self.get_shard_id(shard_key)
        return self.get_engine(shard_id)
    
    def get_session(self, shard_id: int) -> Session:
        """Create a new session for a specific shard."""
        if shard_id not in self._session_factories:
            raise ValueError(f"Shard {shard_id} not found. Available: {list(self._session_factories.keys())}")
        return self._session_factories[shard_id]()
    
    def get_session_for_key(self, shard_key: Union[str, uuid.UUID, int]) -> Session:
        """Create a new session for the shard that handles the given key."""
        shard_id = self.get_shard_id(shard_key)
        return self.get_session(shard_id)
    
    @contextmanager
    def session_scope(self, shard_key: Union[str, uuid.UUID, int]) -> Generator[Session, None, None]:
        """
        Context manager for session management with automatic cleanup.
        
        Usage:
            with shard_manager.session_scope(user_id) as session:
                session.query(...)
        """
        session = self.get_session_for_key(shard_key)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_all_sessions(self) -> Generator[tuple[int, Session], None, None]:
        """
        Get sessions for all shards. Useful for cross-shard queries.
        
        Yields:
            Tuples of (shard_id, session)
        """
        for shard_id in self._session_factories:
            yield shard_id, self.get_session(shard_id)
    
    def get_all_engines(self) -> Dict[int, Engine]:
        """Get all shard engines."""
        return self._engines.copy()
    
    @property
    def num_shards(self) -> int:
        """Return the number of active shards."""
        return self._num_shards
    
    @property
    def shard_ids(self) -> List[int]:
        """Return all shard IDs."""
        return list(self._engines.keys())
    
    def health_check(self) -> Dict[int, bool]:
        """
        Check health of all shard connections.
        
        Returns:
            Dict mapping shard_id to health status (True = healthy)
        """
        results = {}
        for shard_id, engine in self._engines.items():
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                results[shard_id] = True
            except Exception as e:
                logger.error(f"Health check failed for shard {shard_id}: {e}")
                results[shard_id] = False
        return results
    
    def dispose_all(self) -> None:
        """Dispose all engine connections. Call during application shutdown."""
        for shard_id, engine in self._engines.items():
            logger.info(f"Disposing shard {shard_id} connections")
            engine.dispose()
        logger.info("All shard connections disposed")


# Global shard manager instance
@lru_cache(maxsize=1)
def get_shard_manager() -> ShardManager:
    """Get or create the global ShardManager instance."""
    return ShardManager()


def get_sharded_db_by_key(shard_key: Union[str, uuid.UUID, int]) -> Generator[Session, None, None]:
    """
    Dependency function to get a database session for a specific shard key.
    
    Usage:
        @app.get("/users/{user_id}/orders")
        def get_user_orders(
            user_id: uuid.UUID,
            db: Session = Depends(lambda: get_sharded_db_by_key(user_id))
        ):
            ...
    """
    manager = get_shard_manager()
    session = manager.get_session_for_key(shard_key)
    try:
        yield session
    finally:
        session.close()


def get_sharded_db(shard_id: int = 0) -> Generator[Session, None, None]:
    """
    Dependency function to get a database session for a specific shard.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_sharded_db)):
            ...
    """
    manager = get_shard_manager()
    session = manager.get_session(shard_id)
    try:
        yield session
    finally:
        session.close()


class ShardedRepository:
    """
    Base class for repositories that need cross-shard operations.
    
    Provides utilities for:
    - Executing queries across all shards
    - Aggregating results from multiple shards
    - Scatter-gather pattern implementation
    """
    
    def __init__(self):
        self.shard_manager = get_shard_manager()
    
    def scatter_gather(
        self, 
        query_func: callable, 
        aggregate_func: Optional[callable] = None
    ) -> List[Any]:
        """
        Execute a query across all shards and gather results.
        
        Args:
            query_func: Function that takes a session and returns results
            aggregate_func: Optional function to combine results (default: flat list)
            
        Returns:
            Aggregated results from all shards
        """
        all_results = []
        
        for shard_id, session in self.shard_manager.get_all_sessions():
            try:
                results = query_func(session)
                all_results.append((shard_id, results))
            except Exception as e:
                logger.error(f"Query failed on shard {shard_id}: {e}")
                all_results.append((shard_id, []))
            finally:
                session.close()
        
        if aggregate_func:
            return aggregate_func(all_results)
        
        # Default: flatten all results
        flat_results = []
        for _, results in all_results:
            if isinstance(results, list):
                flat_results.extend(results)
            else:
                flat_results.append(results)
        return flat_results
    
    def find_by_id(
        self, 
        model_class: type,
        id_value: Union[str, uuid.UUID, int],
        shard_key: Optional[Union[str, uuid.UUID, int]] = None
    ) -> Optional[Any]:
        """
        Find a record by ID, using shard key if provided.
        
        Args:
            model_class: The SQLAlchemy model class
            id_value: The ID to search for
            shard_key: Optional shard key (if known). If not provided,
                      will search all shards.
        """
        if shard_key:
            # Direct lookup on specific shard
            with self.shard_manager.session_scope(shard_key) as session:
                return session.query(model_class).filter_by(id=id_value).first()
        
        # Search all shards
        def query(session):
            return session.query(model_class).filter_by(id=id_value).first()
        
        results = self.scatter_gather(query)
        return next((r for r in results if r is not None), None)


# Utility functions for common operations

def create_tables_on_all_shards(base: DeclarativeBase) -> None:
    """Create all tables on all shards during application startup."""
    manager = get_shard_manager()
    for shard_id, engine in manager.get_all_engines().items():
        logger.info(f"Creating tables on shard {shard_id}")
        base.metadata.create_all(bind=engine)
    logger.info("Tables created on all shards")


def drop_tables_on_all_shards(base: DeclarativeBase) -> None:
    """Drop all tables on all shards. Use with caution!"""
    manager = get_shard_manager()
    for shard_id, engine in manager.get_all_engines().items():
        logger.warning(f"Dropping tables on shard {shard_id}")
        base.metadata.drop_all(bind=engine)
    logger.warning("Tables dropped on all shards")

