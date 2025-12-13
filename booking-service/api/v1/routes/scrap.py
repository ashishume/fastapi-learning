from core.scrap import (
    UPCOMING_IPO_URL, 
    fetch_html, 
    get_active_ipos, 
    get_closed_ipos, 
    IPO_URL,
    get_all_upcoming_ipos_with_pagination
)
from fastapi import APIRouter
import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

router = APIRouter()


@router.get("/active_ipos")
def get_active_ipos_endpoint():
    return get_active_ipos()


@router.get("/closed_ipos")
def get_closed_ipos_endpoint():
    return get_closed_ipos()


@router.get("/all_ipos")
def get_all_ipos_endpoint():
    return get_active_ipos() + get_closed_ipos()


@router.get("/upcoming_ipos_all")
async def get_all_upcoming_ipos_endpoint(
    include_html: bool = True,
    clean_html: bool = True,
    max_clicks: int = 50,
    debug: bool = True,
):
    """
    Get all upcoming IPOs by handling pagination (Load More button).
    This endpoint uses Playwright to click through all pages.
    
    Args:
        include_html: If True, includes the scraped HTML in the response
        clean_html: If True, removes scripts/styles/etc from returned HTML (better for feeding to LLMs)
        max_clicks: Safety limit to prevent infinite loops
        debug: If True, prints some debugging info to logs
    """
    try:
        result = await get_all_upcoming_ipos_with_pagination(
            return_html=include_html,
            clean_html=clean_html,
            max_clicks=max_clicks,
            debug=debug,
        )

        if include_html:
            ipos, html = result
            return {"success": True, "count": len(ipos), "ipos": ipos, "html": html}

        ipos = result
        return {"success": True, "count": len(ipos), "ipos": ipos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all upcoming IPOs: {str(e)}")


@router.get("/ipos_html")
async def get_ipos_html_endpoint():
    try:
        # Fetch the webpage
        async with httpx.AsyncClient() as client:
            response = await client.get(UPCOMING_IPO_URL, timeout=10.0)
            response.raise_for_status()
        
        # Parse HTML

        soup = BeautifulSoup(response.text, 'html.parser')
        # Find div with id='UpcomingIpo'
        target_div = soup.find('div', id='UpcomingIpo')
        
        if target_div:
            return {
                "success": True,
                "html": str(target_div),
                "text": target_div.get_text(strip=True)
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail="Div with id='UpcomingIpo' not found"
            )
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
