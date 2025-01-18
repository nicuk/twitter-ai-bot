# CryptoRank API Integration

## Overview
The Elion bot uses the CryptoRank API to fetch real-time cryptocurrency market data, including prices, volumes, and market caps.

## API Version
We use the CryptoRank API v1 endpoint: `https://api.cryptorank.io/v1`

## Authentication
- Get your API key from: https://api.cryptorank.io
- Set it in your `.env` file as: `CRYPTORANK_API_KEY=your_api_key_here`

## Important Notes
1. The API key must be passed as a query parameter `api_key`, NOT in the headers
2. Example request:
```python
params = {
    'api_key': 'your_api_key_here',
    'limit': 100  # optional parameters
}
response = requests.get('https://api.cryptorank.io/v1/currencies', params=params)
```

3. Do NOT use the v2 endpoint or header-based authentication as they don't work reliably

## Example Response Structure
```json
{
  "data": [
    {
      "id": 1,
      "rank": 1,
      "slug": "bitcoin",
      "name": "Bitcoin",
      "symbol": "BTC",
      "values": {
        "USD": {
          "price": 104439.40,
          "volume24h": 23031478492,
          "high24h": 105860.64,
          "low24h": 99545.85
        }
      }
    }
  ]
}
```

## Common Endpoints
1. Get Currencies (Top 100):
```python
params = {
    'api_key': api_key,
    'limit': 100,
    'sortBy': 'rank',
    'sortDirection': 'ASC'
}
response = requests.get('https://api.cryptorank.io/v1/currencies', params=params)
```

## Troubleshooting
1. If you get a 401 error, check:
   - API key is set correctly in .env
   - API key is passed as `api_key` in query parameters
   - Using v1 endpoint (not v2)

2. Common Issues:
   - Using `X-Api-Key` in headers (wrong)
   - Using v2 endpoint (wrong)
   - Not passing API key as query parameter (wrong)

## Implementation Files
The API is primarily used in:
- `elion/data_sources.py`: Main API wrapper
- `elion/portfolio.py`: For portfolio tracking
- `elion/market_analysis.py`: For market analysis
