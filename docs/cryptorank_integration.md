# CryptoRank API Integration Guide

## Authentication Solution
The key to getting the CryptoRank API working was:

1. Use **only** the `X-Api-Key` header:
```python
headers = {
    'X-Api-Key': api_key  # Do NOT include Content-Type or other headers
}
```

2. Use the correct parameter names exactly as specified in the API docs:
```python
params = {
    'limit': 100,  # Must be 100, 500, or 1000
    'sortBy': 'rank',  # Not sort[by]
    'sortDirection': 'ASC'  # Not sort[dir]
}
```

## Finding Alpha Opportunities
To find real alpha opportunities (not just top coins), we should:

1. Filter for coins with:
   - Market cap between $1M and $100M
   - 24h volume > $100K
   - Significant price movement (>5% in 24h)
   - Recent listing date (within last 3 months)

2. Sort by:
   - Volume growth
   - Price momentum
   - Market cap growth

## Finding Shill Opportunities
For potential shill opportunities:

1. Filter for coins with:
   - Market cap under $50M
   - 24h volume between $100K and $1M
   - Price stability (not too volatile)
   - Strong fundamentals (check funding rounds)

2. Sort by:
   - Recent price action
   - Volume growth
   - Community growth

## API Endpoints Used
1. `/v2/currencies` - Get list of currencies with market data
2. `/v2/currencies/funding-rounds` - Get funding data
3. `/v2/currencies/{id}/full-metadata` - Get detailed coin data

## Error Handling
Always check response status and handle common errors:
```python
try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    if hasattr(e.response, 'text'):
        print(f"Response: {e.response.text}")
    return {}
```
