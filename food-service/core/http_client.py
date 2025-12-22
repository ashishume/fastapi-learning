"""HTTP client utility for making requests to other microservices."""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, status
import httpx  # pyright: ignore[reportMissingImports]

# Service URLs from environment variables
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8002")


async def fetch_from_service(
    url: str,
    request: Request,
    method: str = "GET",
    json_data: Optional[Dict[str, Any]] = None,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """
    Generic function to make HTTP requests to other services.
    
    Args:
        url: Full URL to the service endpoint
        request: FastAPI Request object to extract auth token
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        json_data: Optional JSON payload for POST/PUT requests
        timeout: Request timeout in seconds
        
    Returns:
        Dict containing the JSON response from the service
        
    Raises:
        HTTPException: If the request fails or returns non-2xx status
    """
    try:
        async with httpx.AsyncClient() as client:
            token = request.cookies.get("access_token")
            cookies = {"access_token": token} if token else {}
            headers = {"Content-Type": "application/json"}
            
            # Make the request based on method
            if method.upper() == "GET":
                response = await client.get(
                    url, cookies=cookies, headers=headers, timeout=timeout, follow_redirects=True
                )
            elif method.upper() == "POST":
                response = await client.post(
                    url, cookies=cookies, headers=headers, json=json_data, timeout=timeout, follow_redirects=True
                )
            elif method.upper() == "PUT":
                response = await client.put(
                    url, cookies=cookies, headers=headers, json=json_data, timeout=timeout, follow_redirects=True
                )
            elif method.upper() == "DELETE":
                response = await client.delete(
                    url, cookies=cookies, headers=headers, timeout=timeout, follow_redirects=True
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported HTTP method: {method}",
                )
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Service error: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


async def fetch_product(product_id: int, request: Request) -> Dict[str, Any]:
    """
    Fetch product details from product service.
    
    Args:
        product_id: ID of the product to fetch
        request: FastAPI Request object
        
    Returns:
        Dict containing product details
    """
    url = f"{PRODUCT_SERVICE_URL}/product/items/{product_id}"
    return await fetch_from_service(url, request)


async def fetch_category(category_id: int, request: Request) -> Dict[str, Any]:
    """
    Fetch category details from product service.
    
    Args:
        category_id: ID of the category to fetch
        request: FastAPI Request object
        
    Returns:
        Dict containing category details
    """
    url = f"{PRODUCT_SERVICE_URL}/product/categories/{category_id}"
    return await fetch_from_service(url, request)


async def fetch_user(request: Request) -> Dict[str, Any]:
    """
    Fetch user details from auth service.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Dict containing user details
    """
    url = f"{AUTH_SERVICE_URL}/auth/user_details"
    return await fetch_from_service(url, request)


async def fetch_inventory_item(inventory_id: int, request: Request) -> Dict[str, Any]:
    """
    Fetch inventory item details from inventory service.
    
    Args:
        inventory_id: ID of the inventory item to fetch
        request: FastAPI Request object
        
    Returns:
        Dict containing inventory item details
    """
    url = f"{INVENTORY_SERVICE_URL}/inventory/inventory/{inventory_id}"
    return await fetch_from_service(url, request)

