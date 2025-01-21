# ELAI AI Trading Bot

## Project Status: Pre-Deployment Testing

### Latest Updates (2025-01-17)
- Completed major refactoring of ELAI class structure
- Separated functionality into dedicated components
- Enhanced market analysis capabilities
- Improved personality and engagement systems

### Project Structure
```
elai/
├── core/
│   └── elai.py              # Main orchestrator
├── personality/
│   └── traits.py             # Personality system
└── twitter/                  # Twitter API handling
    ├── api_client.py         # API client
    ├── bot.py                # Bot implementation
    └── rate_limiter.py       # Rate limiting

strategies/
├── trend_strategy.py         # Trend analysis + content generation
├── volume_strategy.py        # Volume analysis + content generation
└── shared_utils.py           # Common utilities
```

### Components
1. **ELAI Core (core/elai.py)**
   - Orchestrates all components
   - Integrates strategies with personality
   - Manages tweet generation and timing
   - Tracks daily tweet limits and performance

2. **Strategies**
   - **Trend Strategy**: Market trend analysis and content generation
   - **Volume Strategy**: Volume analysis and content generation
   - **Shared Utils**: Common utilities for data fetching and analysis

3. **Personality System**
   - Manages bot's personality traits
   - Handles engagement style
   - Adapts tone based on market conditions
   - Provides consistent bot character

4. **Twitter Integration**
   - API client for Twitter interactions
   - Rate limiting implementation
   - Bot implementation for posting

5. **Future Components (Not Currently Integrated)**
   - Portfolio Management
   - Extended Data Sources
   - Additional Engagement Features

### Development Environment Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/elai-bot.git
cd elai-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/elai-ai.git
cd elai-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your API keys and configuration
```

Required API Keys:
- Twitter API (v2)
- Meta Llama API
- CryptoRank API

### Usage

1. Test the setup:
```bash
python test_twitter_api.py  # Test Twitter API connection
python demo_tweets.py       # Test tweet generation
```

2. Run ELAI:
```bash
python main.py
```

### Development

1. Run tests:
```bash
pytest
```

2. Format code:
```bash
black .
isort .
```

3. Type checking:
```bash
mypy .
```

### Documentation
- [Setup Guide](docs/SETUP.md)
- [API Integration & Security](docs/API_INTEGRATION.md)
- [Development Status](DEVELOPMENT_STATUS.md)

### Deployment

#### Prerequisites
1. A Twitter Developer Account with API access
2. A CryptoRank API account
3. An LLM API key (e.g., Meta Llama 2)
4. A Railway account

#### Setup GitHub Actions Secrets
Before deploying, you need to set up the following secrets in your GitHub repository:

1. Go to your repository's Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Add the following secrets:
   - `TWITTER_API_KEY`: Your Twitter API Key
   - `TWITTER_API_SECRET`: Your Twitter API Secret
   - `TWITTER_ACCESS_TOKEN`: Your Twitter Access Token
   - `TWITTER_ACCESS_SECRET`: Your Twitter Access Secret
   - `CRYPTORANK_API_KEY`: Your CryptoRank API Key
   - `LLM_API_KEY`: Your LLM API Key
   - `RAILWAY_TOKEN`: Your Railway Deployment Token (Get this from Railway Dashboard > Project Settings > Service > Tokens)

#### Deploy to Railway
1. Fork this repository
2. Set up the required GitHub Actions secrets
3. Push to the main branch
4. GitHub Actions will automatically:
   - Run tests
   - Deploy to Railway if tests pass

### Testing Plan
1. **Unit Tests**
   - Component-level testing
   - Mock external dependencies
   - Test core functionality

2. **Integration Tests**
   - Component interaction testing
   - Data flow validation
   - Error handling verification

3. **System Tests**
   - End-to-end functionality
   - Performance testing
   - Load testing

### Railway Deployment Steps
1. **Prerequisites**
   - Railway account
   - Railway CLI installed
   - Project configured in Railway

2. **Configuration**
   - Set up environment variables
   - Configure deployment settings
   - Set up monitoring

3. **Deployment Commands**
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Deploy project
railway up
```

### Git Commands Reference
```bash
# Initialize repository
git init

# Add files
git add .

# Commit changes
git commit -m "commit message"

# Create and switch to new branch
git checkout -b branch-name

# Push changes
git push origin branch-name
```

### Python Commands Reference
```bash
# Run tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_market_analyzer.py

# Run with coverage
python -m pytest --cov=elai tests/

# Start the bot
python main.py
```

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

### License
MIT License - See LICENSE file for details

---
Last Updated: 2025-01-17
