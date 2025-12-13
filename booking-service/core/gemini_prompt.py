def get_gemini_prompt(html_content: str) -> str:
    return f"""You are given scraped HTML from Moneycontrol that lists upcoming IPOs.  
Your task is to extract IPO information and also enrich it with additional company and financial details, even if those details are not present in the HTML.

### INPUT HTML
{html_content}

### TASKS
1. Parse the HTML and extract all IPO cards.
2. For each IPO, create a JSON object with the following fields:
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

3. For each IPO, fetch or infer **additional financial details** from public sources (not from the HTML):
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

4. Output should be strictly valid **JSON** in the following format:

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
- Ensure extracted fields are correct and clean.
- Fill missing financial data using reliable external info sources.
- If some data is not publicly available, set it as null instead of guessing.
"""
