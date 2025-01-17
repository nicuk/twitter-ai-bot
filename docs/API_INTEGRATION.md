# API Integration and Security Documentation

## API Key Management

All sensitive API keys and credentials are managed securely through environment variables using the following approach:

1. **Environment Variables**
   - All API keys are stored in `.env` file (not committed to git)
   - A `.env.template` file provides the structure without actual keys
   - Railway deployment uses secure environment variable storage

2. **Required API Keys**
   ```
   # Twitter API Credentials
   TWITTER_CLIENT_ID=
   TWITTER_CLIENT_SECRET=
   TWITTER_ACCESS_TOKEN=
   TWITTER_ACCESS_TOKEN_SECRET=
   TWITTER_BEARER_TOKEN=

   # Meta Llama API
   AI_API_URL=https://api-user.ai.aitech.io/api/v1/user/products/209/use
   AI_ACCESS_TOKEN=[your_meta_llama_token]

   # Market Data
   CRYPTORANK_API_KEY=
   ```

## Meta Llama Integration

The bot uses Meta Llama 3.2 (7B parameters) for advanced language processing. This integration is configured in `model_providers.py`:

```python
META_LLAMA_PROVIDER = {
    "MetaLlama": {
        "component_class": "MetaLlamaComponent",
        "inputs": [
            {
                "name": "model_name",
                "display_name": "Model Name",
                "options": ["Meta-Llama-3.2-7B-Instruct"],
                "value": "Meta-Llama-3.2-7B-Instruct",
            },
            {
                "name": "api_base",
                "display_name": "API Base URL",
                "value": "https://api-user.ai.aitech.io/api/v1/user/products/209/use",
            }
        ]
    }
}
```

### Meta Llama Features Used:

1. **Market Analysis**
   - Sentiment analysis of market trends
   - Technical analysis interpretation
   - Pattern recognition in price movements

2. **Content Generation**
   - Tweet composition with personality
   - Response generation for community engagement
   - Alpha insight formulation

3. **Project Analysis**
   - Fundamental analysis of crypto projects
   - Risk assessment
   - Technical evaluation

## Security Measures

1. **API Key Protection**
   - Keys are never hardcoded in source code
   - Keys are not logged or exposed in error messages
   - Separate development and production keys

2. **Rate Limiting**
   - Built-in rate limit handling for all APIs
   - Automatic backoff on API limits
   - Failed requests are retried with exponential backoff

3. **Error Handling**
   - All API calls are wrapped in try-except blocks
   - Errors are logged without exposing sensitive data
   - Graceful degradation when APIs are unavailable

## Usage in Production

The bot is deployed on Railway with the following security measures:

1. **Environment Variables**
   - All API keys are stored as Railway environment variables
   - Keys are encrypted at rest
   - Keys are never exposed in logs

2. **Access Control**
   - Limited access to production environment
   - Key rotation policies in place
   - Regular security audits

3. **Monitoring**
   - API usage monitoring
   - Rate limit tracking
   - Error rate monitoring

## Development Guidelines

When working with APIs:

1. Always use environment variables for credentials
2. Never commit API keys to version control
3. Use the provided API wrapper classes
4. Follow rate limit guidelines
5. Implement proper error handling
6. Log errors without exposing sensitive data
