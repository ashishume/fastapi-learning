"""
HTML Parser for extracting structured IPO data from Moneycontrol HTML.
This parser extracts only relevant IPO information to reduce token usage for LLM processing.
Specifically designed for Moneycontrol's IPO card structure.
"""

import re
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


def extract_ipo_data_from_html(html_content: str) -> List[Dict]:
    """
    Extract structured IPO data from HTML content.
    This significantly reduces token usage by extracting only relevant information.
    
    Args:
        html_content: Raw HTML content from Moneycontrol IPO page
        
    Returns:
        List of dictionaries containing structured IPO data
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, "html.parser")
    ipos = []
    
    # Find the main container (div#UpcomingIpo or similar)
    main_container = soup.find("div", id=re.compile(r"UpcomingIpo|Ipo", re.I))
    if not main_container:
        main_container = soup
    
    # Find all IPO card holders - Moneycontrol uses class containing "ipoInfoCardholder"
    card_holders = main_container.find_all("div", class_=re.compile(r"ipoInfoCardholder", re.I))
    
    if card_holders:
        # Use specific Moneycontrol structure parser
        for card_holder in card_holders:
            ipo = _parse_moneycontrol_card(card_holder)
            if ipo and ipo.get("companyName"):
                ipos.append(ipo)
    else:
        # Fallback to generic parsing
        ipos = _parse_generic_structure(soup)
    
    return ipos


def _parse_moneycontrol_card(card_holder) -> Optional[Dict]:
    """
    Parse a single Moneycontrol IPO card structure.
    
    Structure:
    - RHP link (class "rhpBtn")
    - Main card link (class "ipoGrayCard")
    - Category buttons (Mainline/SME, Upcoming/Open/Closed)
    - Company name in h2 (class "cardTitle")
    - Description paragraph
    - Details table (Open Date, Close Date, Issue Price, Lot Size, Issue Size)
    - Subscription table (QIB, Retail, NII, Others, Total)
    - IPO Dates section (ul/li with important dates)
    """
    ipo = {}
    
    # Extract RHP link
    rhp_link = card_holder.find("a", class_=re.compile(r"rhpBtn", re.I))
    if rhp_link and rhp_link.get("href"):
        ipo["rhpUrl"] = rhp_link.get("href", "").strip()
    
    # Extract main card link (detail page)
    main_card = card_holder.find("a", class_=re.compile(r"ipoGrayCard", re.I))
    if main_card and main_card.get("href"):
        ipo["detailPageUrl"] = main_card.get("href", "").strip()
    
    # Extract category and type from buttons
    buttons = card_holder.find_all("button", class_=re.compile(r"btnEle", re.I))
    for button in buttons:
        text = button.get_text(strip=True)
        classes = button.get("class", [])
        class_str = " ".join(classes).lower()
        
        if text.lower() in ["mainline", "sme"]:
            ipo["category"] = text
        elif text.lower() in ["upcoming", "open", "closed"]:
            ipo["type"] = text
    
    # Extract company name from h2 with class "cardTitle"
    title_elem = card_holder.find("h2", class_=re.compile(r"cardTitle", re.I))
    if title_elem:
        company_text = title_elem.get_text(strip=True)
        # Remove "IPO" suffix if present
        company_text = re.sub(r"\s+IPO\s*$", "", company_text, flags=re.I)
        ipo["companyName"] = company_text
        ipo["ipoName"] = company_text  # Same as company name
    
    # Extract description paragraph (use as fallback if table data is missing)
    desc_elem = card_holder.find("p", class_=re.compile(r"description", re.I))
    if desc_elem:
        desc_text = desc_elem.get_text()
        # Extract dates from description (only if not already set from table)
        if "openDate" not in ipo:
            date_matches = re.findall(r"(\d{4}-\d{2}-\d{2})", desc_text)
            if len(date_matches) >= 2:
                ipo["openDate"] = date_matches[0]
                ipo["closeDate"] = date_matches[1]
            elif len(date_matches) == 1:
                ipo["openDate"] = date_matches[0]
        
        # Extract price band from description (only if not already set from table)
        if "priceBand" not in ipo:
            price_match = re.search(r"price\s*band\s*is\s*set\s*at\s*(\d+)\s*(?:to\s*(\d+))?", desc_text, re.I)
            if price_match:
                if price_match.group(2):
                    ipo["priceBand"] = f"₹{price_match.group(1)} - ₹{price_match.group(2)}"
                else:
                    ipo["priceBand"] = f"₹{price_match.group(1)}"
    
    # Parse Details table
    details_table = card_holder.find("table", class_=re.compile(r"detailTable", re.I))
    if details_table:
        _parse_details_table(details_table, ipo)
    
    # Parse Subscription table
    subscription_table = card_holder.find("table", class_=re.compile(r"subscriptionTable", re.I))
    if subscription_table:
        _parse_subscription_table(subscription_table, ipo)
    
    # Parse IPO Dates section
    dates_section = card_holder.find("div", class_=re.compile(r"ipoDtSteps", re.I))
    if dates_section:
        _parse_ipo_dates_section(dates_section, ipo)
    
    # Build links object if we have URLs
    links = {}
    if ipo.get("rhpUrl"):
        links["rhpUrl"] = ipo.pop("rhpUrl")
    if ipo.get("detailPageUrl"):
        links["detailPageUrl"] = ipo.pop("detailPageUrl")
    if links:
        ipo["links"] = links
    
    # Clean empty values
    ipo = {k: v for k, v in ipo.items() if v and v != "" and v != "NA"}
    
    return ipo if ipo.get("companyName") else None


def _parse_details_table(table, ipo: Dict):
    """Parse the Details table (Open Date, Close Date, Issue Price, Lot Size, Issue Size)."""
    rows = table.find_all("tr")
    
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        
        label = cells[0].get_text(strip=True).lower()
        value = cells[1].get_text(strip=True)
        
        if not value or value == "NA" or value == "":
            continue
        
        if "open date" in label:
            # Prefer YYYY-MM-DD format, but also handle "DD MMM, YYYY" format
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", value)
            if date_match:
                ipo["openDate"] = date_match.group(1)
            else:
                # Try to parse "16 Dec, 2025" format
                date_match = re.search(r"(\d{1,2})\s+(\w+),?\s+(\d{4})", value)
                if date_match:
                    # Keep original format for now, LLM can handle it
                    ipo["openDate"] = value
                else:
                    ipo["openDate"] = value
        elif "close date" in label:
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", value)
            if date_match:
                ipo["closeDate"] = date_match.group(1)
            else:
                date_match = re.search(r"(\d{1,2})\s+(\w+),?\s+(\d{4})", value)
                if date_match:
                    ipo["closeDate"] = value
                else:
                    ipo["closeDate"] = value
        elif "issue price" in label:
            ipo["priceBand"] = value
        elif "lot size" in label:
            # Only add if not empty
            if value.strip():
                ipo["lotSize"] = value
        elif "issue size" in label:
            ipo["issueSize"] = value


def _parse_subscription_table(table, ipo: Dict):
    """Parse the Subscription table (QIB, Retail, NII, Others, Total)."""
    subscription = {}
    rows = table.find_all("tr")
    
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        
        label = cells[0].get_text(strip=True).lower()
        value = cells[1].get_text(strip=True)
        
        if "qualified institutional" in label or "qib" in label:
            subscription["qib"] = value if value and value != "Awaiting" else ""
        elif "retail individual" in label or "retail" in label:
            subscription["retail"] = value if value and value != "Awaiting" else ""
        elif "non-institutional" in label or "nii" in label:
            subscription["nii"] = value if value and value != "Awaiting" else ""
        elif "others" in label and "total" not in label:
            subscription["others"] = value if value and value != "Awaiting" else ""
        elif "total" in label:
            subscription["total"] = value if value and value != "Awaiting" else ""
    
    # Only add subscription if we have at least one value
    if subscription and any(v for v in subscription.values()):
        ipo["subscription"] = subscription


def _parse_ipo_dates_section(dates_section, ipo: Dict):
    """Parse the IPO Dates section (ul/li with important dates)."""
    important_dates = {}
    date_items = dates_section.find_all("li")
    
    for item in date_items:
        spans = item.find_all("span")
        if len(spans) >= 2:
            date_str = spans[0].get_text(strip=True)
            label = spans[1].get_text(strip=True).lower()
            
            if date_str and date_str != "NA":
                if "basis of allotment" in label:
                    important_dates["basisOfAllotment"] = date_str
                elif "initiation of refunds" in label or "refund" in label:
                    important_dates["refundInitiation"] = date_str
                elif "credit of shares" in label or "credit" in label:
                    important_dates["creditOfShares"] = date_str
                elif "listing date" in label or "listing" in label:
                    important_dates["listingDate"] = date_str
    
    if important_dates:
        ipo["importantDates"] = important_dates


def _parse_generic_structure(soup: BeautifulSoup) -> List[Dict]:
    """Fallback parser for generic HTML structures."""
    ipos = []
    
    # Look for any divs with IPO-related content
    ipo_sections = soup.find_all(["div", "li", "tr"], 
                                 string=re.compile(r"ipo|company|issue", re.I))
    
    for section in ipo_sections[:50]:  # Limit to prevent too many results
        text = section.get_text()
        
        # Check if this looks like IPO data
        if not (re.search(r"company|ipo|issue|price", text, re.I)):
            continue
        
        ipo = {}
        
        # Extract company name (first capitalized word sequence)
        company_match = re.search(r"([A-Z][a-zA-Z\s&]+(?:Limited|Ltd|Inc|Corp|Corporation)?)", text)
        if company_match:
            ipo["companyName"] = company_match.group(1).strip()
        
        # Extract dates
        dates = re.findall(r"(\d{4}-\d{2}-\d{2})", text)
        if dates:
            ipo["openDate"] = dates[0] if dates else ""
            ipo["closeDate"] = dates[1] if len(dates) > 1 else dates[0] if dates else ""
        
        # Extract price band
        price_match = re.search(r"₹?\s*(\d+)\s*[-–]\s*₹?\s*(\d+)", text)
        if price_match:
            ipo["priceBand"] = f"₹{price_match.group(1)} - ₹{price_match.group(2)}"
        
        # Clean and add
        ipo = {k: v for k, v in ipo.items() if v}
        if ipo.get("companyName"):
            ipos.append(ipo)
    
    return ipos


def format_ipo_data_for_llm(ipos: List[Dict]) -> str:
    """
    Format extracted IPO data into a compact JSON string for LLM processing.
    This reduces token usage significantly compared to raw HTML.
    
    Args:
        ipos: List of IPO dictionaries
        
    Returns:
        JSON string representation of IPO data
    """
    if not ipos:
        return json.dumps({"ipos": []}, indent=2, ensure_ascii=False)
    
    # Create a compact representation
    formatted = {
        "ipos": ipos
    }
    
    return json.dumps(formatted, indent=2, ensure_ascii=False)


def get_structured_ipo_data(html_content: str) -> str:
    """
    Main function to extract and format IPO data from HTML.
    Returns structured JSON string ready for LLM processing.
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        JSON string with structured IPO data
    """
    ipos = extract_ipo_data_from_html(html_content)
    return format_ipo_data_for_llm(ipos)
