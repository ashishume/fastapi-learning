from core.html_scrap import (
    get_all_upcoming_ipos_with_pagination
)
from core.html_parser import get_structured_ipo_data
from core.gemini_service import get_gemini_service
from fastapi import APIRouter
from fastapi import HTTPException
from typing import Optional
from pydantic import BaseModel
from core.gemini_prompt import get_gemini_prompt

router = APIRouter()


class GeminiProcessRequest(BaseModel):
    """Request model for Gemini HTML processing."""
    html_content: str
    prompt: Optional[str] = None
    model_name: str = "gemini-1.5-flash"
    extract_structured: bool = False


@router.get("/upcoming_ipos")
async def get_all_upcoming_ipos_endpoint(
    include_html: bool = False,
    clean_html: bool = True,
    max_clicks: int = 50,
    debug: bool = True,
    use_gemini: bool = False,
    gemini_model: str = "gemini-2.5-flash",
):
    """
    Get all upcoming IPOs by handling pagination (Load More button).
    This endpoint uses Playwright to click through all pages.
    
    Args:
        include_html: If True, includes the scraped HTML in the response
        clean_html: If True, removes scripts/styles/etc from returned HTML (better for feeding to LLMs)
        max_clicks: Safety limit to prevent infinite loops
        debug: If True, prints some debugging info to logs
        use_gemini: If True, processes the HTML content with Gemini LLM
        gemini_prompt: Optional custom prompt for Gemini. If not provided, uses default prompt
        gemini_model: Gemini model to use (default: gemini-1.5-flash)
    """
    try:
        result = await get_all_upcoming_ipos_with_pagination(
            return_html=include_html or use_gemini,  # Need HTML if using Gemini
            clean_html=clean_html,
            max_clicks=max_clicks,
            debug=debug,
        )

        response_data = {"success": True}
        
        if include_html or use_gemini:
            ipos, html = result
            response_data["count"] = len(ipos)
            response_data["ipos"] = ipos
            
            if include_html:
                response_data["html"] = html
            
            # Process with Gemini if requested
            if use_gemini:
                try:
                    # Parse HTML to extract structured data (reduces tokens by 60-80%)
                    structured_data = get_structured_ipo_data(html)
                    
                    gemini_service = get_gemini_service(model_name=gemini_model)
                    if gemini_service:
                        gemini_response = gemini_service.process_html(
                            html_content=structured_data,  # Pass structured data instead of raw HTML
                            prompt=get_gemini_prompt(structured_data=structured_data),
                            parse_json=True
                        )
                        # If the response is a list, wrap it in an object with "ipos" key
                        # If it's already a dict with "ipos", use it as is
                        if isinstance(gemini_response, list):
                            response_data["gemini_analysis"] = {"ipos": gemini_response}
                        elif isinstance(gemini_response, dict):
                            response_data["gemini_analysis"] = gemini_response
                        else:
                            # Fallback to string if parsing failed
                            response_data["gemini_analysis"] = gemini_response
                    else:
                        response_data["gemini_error"] = "Gemini service is not available. Please check GEMINI_API_KEY environment variable."
                except Exception as e:
                    response_data["gemini_error"] = f"Error processing with Gemini: {str(e)}"
            
            return response_data
        else:
            ipos = result
            response_data["count"] = len(ipos)
            response_data["ipos"] = ipos
            return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all upcoming IPOs: {str(e)}")

