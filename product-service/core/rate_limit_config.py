
import os
from typing import Dict, Tuple


class RateLimitConfig:
    
    # ===== Global Settings =====
    
    # Master switch - set to False to disable all rate limiting
    ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # Default limits applied when no specific limit is set
    DEFAULT_LIMIT: int = int(os.getenv("RATE_LIMIT_DEFAULT_LIMIT", "100"))
    DEFAULT_WINDOW: int = int(os.getenv("RATE_LIMIT_DEFAULT_WINDOW", "60"))  # seconds
    
    # ===== Per-Endpoint Limits =====
    # Format: "METHOD:PATH": (limit, window_seconds)
    # This allows fine-grained control over different endpoints
    
    ENDPOINT_LIMITS: Dict[str, Tuple[int, int]] = {
        # Items endpoints
        "GET:/items": (200, 60),           # 200 requests per minute for listing items
        "POST:/items": (50, 60),           # 50 requests per minute for creating items
        "PUT:/items/{item_id}": (100, 60), # 100 updates per minute
        "DELETE:/items/{item_id}": (30, 60), # 30 deletions per minute
        
        # Categories endpoints
        "GET:/categories": (150, 60),      # 150 requests per minute for categories
        "POST:/categories": (30, 60),      # 30 new categories per minute
        
        # Root endpoint (health check) - more lenient
        "GET:/": (500, 60),                # 500 requests per minute
        
        # Docs endpoints - very lenient for development
        "GET:/docs": (1000, 60),
        "GET:/redoc": (1000, 60),
        "GET:/openapi.json": (1000, 60),
    }
    
    # ===== Per-HTTP-Method Default Limits =====
    # Applied when endpoint is not in ENDPOINT_LIMITS
    # GET requests typically more frequent than mutations
    
    METHOD_LIMITS: Dict[str, Tuple[int, int]] = {
        "GET": (200, 60),      # 200 GET requests per minute
        "POST": (50, 60),      # 50 POST requests per minute
        "PUT": (100, 60),      # 100 PUT requests per minute
        "PATCH": (100, 60),    # 100 PATCH requests per minute
        "DELETE": (30, 60),    # 30 DELETE requests per minute
    }
    
    # ===== Special Settings =====
    
    # IP addresses that bypass rate limiting (e.g., internal services, monitoring)
    # Format: ["192.168.1.100", "10.0.0.5"]
    WHITELIST_IPS: list = os.getenv("RATE_LIMIT_WHITELIST_IPS", "").split(",")
    WHITELIST_IPS = [ip.strip() for ip in WHITELIST_IPS if ip.strip()]
    
    # User IDs that bypass rate limiting (e.g., admin accounts)
    WHITELIST_USERS: list = os.getenv("RATE_LIMIT_WHITELIST_USERS", "").split(",")
    WHITELIST_USERS = [user.strip() for user in WHITELIST_USERS if user.strip()]
    
    # Fail-open or fail-closed when Redis is unavailable?
    # True = Allow requests when Redis is down (fail-open, recommended for production)
    # False = Deny requests when Redis is down (fail-closed, more secure)
    FAIL_OPEN: bool = os.getenv("RATE_LIMIT_FAIL_OPEN", "true").lower() == "true"
    
    # ===== Advanced Settings =====
    
    # Whether to include query parameters in endpoint identification
    # False = /items?page=1 and /items?page=2 use same limit (recommended)
    # True = Different query params use separate limits
    INCLUDE_QUERY_PARAMS: bool = False
    
    # Different limits for authenticated vs anonymous users
    # Authenticated users might get higher limits
    AUTHENTICATED_MULTIPLIER: float = float(
        os.getenv("RATE_LIMIT_AUTH_MULTIPLIER", "1.5")
    )
    
    @classmethod
    def get_limit_for_endpoint(
        cls,
        method: str,
        path: str,
        is_authenticated: bool = False
    ) -> Tuple[int, int]:
       
        # Create endpoint key
        endpoint_key = f"{method.upper()}:{path}"
        
        # Check for endpoint-specific limit
        if endpoint_key in cls.ENDPOINT_LIMITS:
            limit, window = cls.ENDPOINT_LIMITS[endpoint_key]
        # Check for method-specific default
        elif method.upper() in cls.METHOD_LIMITS:
            limit, window = cls.METHOD_LIMITS[method.upper()]
        # Use global default
        else:
            limit, window = cls.DEFAULT_LIMIT, cls.DEFAULT_WINDOW
        
        # Apply authenticated user multiplier if applicable
        if is_authenticated and cls.AUTHENTICATED_MULTIPLIER > 1.0:
            limit = int(limit * cls.AUTHENTICATED_MULTIPLIER)
        
        return limit, window
    
    @classmethod
    def is_whitelisted(cls, identifier: str) -> bool:
        # Check IP whitelist
        if identifier.startswith("ip:"):
            ip = identifier[3:]  # Remove "ip:" prefix
            return ip in cls.WHITELIST_IPS
        
        # Check user whitelist
        if identifier.startswith("user:"):
            user = identifier[5:]  # Remove "user:" prefix
            return user in cls.WHITELIST_USERS
        
        return False


