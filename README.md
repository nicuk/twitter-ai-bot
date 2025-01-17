# Elion - AI Crypto Trading Assistant

Elion is a sophisticated AI-powered crypto trading and analysis bot that combines market intelligence with a unique personality to provide insights, trading signals, and portfolio management.

## Core Features

- **Unique AI Personality**: Elion has a distinct personality that evolves based on market conditions and interactions
- **Market Analysis**: Real-time market data analysis and trend detection
- **Gem Detection**: Identifies promising low-cap opportunities
- **Portfolio Management**: Tracks and manages positions with sophisticated sizing
- **Shill Review**: Analyzes and rates user-suggested projects
- **Natural Interaction**: Engages with users in a quirky, tech-savvy manner

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API credentials:
   - Copy `.env.template` to a new file named `.env`
   - Configure your API keys for:
     - Twitter API
     - CryptoRank API
     - Other market data sources
   - Fill in your credentials in the `.env` file

3. Initialize the database:
```bash
python -m elion.data_storage
```

4. Run Elion:
```bash
python run_elion.py
```

## Project Structure

- `elion/`
  - `elion.py`: Core bot functionality
  - `personality.py`: AI personality and response generation
  - `data_storage.py`: Database management
  - `data_sources.py`: Market data integration
  - `portfolio.py`: Portfolio tracking and management
  - `project_analysis.py`: Project evaluation logic
  - `engagement.py`: User interaction handling

## Development Status

Check `DEVELOPMENT_STATUS.md` for detailed information about:
- Current development progress
- Component status
- Recent changes
- Pending tasks
- Known issues

## Testing

Run the test suite:
```bash
python -m unittest tests/test_elion.py -v
```

## Important Notes

- Monitor API usage to stay within rate limits
- Keep API keys secure
- Regular database backups recommended
- See `DEVELOPMENT_STATUS.md` for known issues and limitations

## Contributing

1. Check `DEVELOPMENT_STATUS.md` for current status and pending tasks
2. Follow the existing code style and documentation patterns
3. Add tests for new functionality
4. Update documentation as needed

## License

MIT License - See LICENSE file for details
