def get_gemini_prompt(structured_data: str) -> str:
    """
    Generate prompt for Gemini LLM using structured IPO data instead of raw HTML.
    This significantly reduces token usage (60-80% reduction).
    
    Args:
        structured_data: JSON string containing structured IPO data extracted from HTML
        
    Returns:
        Formatted prompt string
    """
    return f"""You are given structured IPO data extracted from Moneycontrol's upcoming IPOs page.
Your task is to enrich this data with additional company and financial details from public sources.

### INPUT DATA (Structured IPO Information)
{structured_data}

### TASKS
1. For each IPO in the input data, enrich it with the following fields:
   - companyName
   - ipoName
   - category (Mainline / SME)
   - type (Upcoming / Open / Closed)
   - openDate
   - closeDate
   - priceBand
   - lotSize
   - issueSize
   - subscription:
       - qib
       - retail
       - nii
       - others
       - total
   - importantDates:
       - basisOfAllotment
       - refundInitiation
       - creditOfShares
       - listingDate
   - links:
       - rhpUrl
       - detailPageUrl

2. For each IPO, fetch or infer **additional financial details** from public sources:
   - companyOverview: short summary of what the company does
   - revenue (last 3 years)
   - profitLoss (last 3 years)
   - marginTrends
   - keyRisks
   - keyStrengths
   - peerComparison (list similar listed companies)
   - useOfFunds
   - managementDetails
   - greyMarketPremium (if available)

3. Output should be strictly valid **JSON** in the following format:

{{
  "ipos": [
    {{
      "companyName": "",
      "ipoName": "",
      "category": "",
      "type": "",
      "openDate": "",
      "closeDate": "",
      "priceBand": "",
      "lotSize": "",
      "issueSize": "",
      "subscription": {{
        "qib": "",
        "retail": "",
        "nii": "",
        "others": "",
        "total": ""
      }},
      "importantDates": {{
        "basisOfAllotment": "",
        "refundInitiation": "",
        "creditOfShares": "",
        "listingDate": ""
      }},
      "links": {{
        "rhpUrl": "",
        "detailPageUrl": ""
      }},
      "financials": {{
        "companyOverview": "",
        "revenue": "",
        "profitLoss": "",
        "marginTrends": "",
        "keyRisks": [],
        "keyStrengths": [],
        "peerComparison": [],
        "useOfFunds": "",
        "managementDetails": "",
        "greyMarketPremium": ""
      }}
    }}
  ]
}}

### RULES
- Only return JSON. No explanations.
- Preserve all existing data from the input (companyName, dates, priceBand, etc.).
- Enrich with financial data using reliable external info sources.
- If some data is not publicly available, set it as null instead of guessing.
- Maintain the same structure and order of IPOs as in the input.
"""
