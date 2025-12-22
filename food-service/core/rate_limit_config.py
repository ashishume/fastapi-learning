"""Rate limiting configuration."""

import os

class RateLimitConfig:
    """Configuration for rate limiting feature."""
    
    # Enable/disable rate limiting globally
    ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # Default rate limit settings
    DEFAULT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    DEFAULT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

