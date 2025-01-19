# Elion AI - Twitter Trading Bot

A modular implementation of an AI trading personality for Twitter.

## Project Structure

```
elion/
├── __init__.py          # Package initialization
├── personality.py       # Core personality traits and characteristics
├── tweet_components.py  # Tweet generation and components
├── engagement.py        # Engagement management and rate limiting
└── elion.py            # Main Elion class combining all components
```

## Components

### ElionCore (personality.py)
- Core personality traits and characteristics
- Response prompts and templates
- Identity and behavioral traits

### TweetComponents (tweet_components.py)
- Tweet generation utilities
- Hooks, transitions, and closers
- Content strategy management

### EngagementManager (engagement.py)
- Rate limiting and post timing
- Tweet history tracking
- Engagement optimization

### Elion (elion.py)
- Main class combining all components
- High-level interaction methods
- Response generation

## Usage

```python
from elion.elion import Elion

# Create Elion instance
elion = Elion()

# Generate response
response = elion.generate_response(context="alpha", content="Market signal detected")

# Find engagement opportunities
opportunities = elion.find_engagement_opportunities()
```

## Testing

Run tests using:
```bash
python -m unittest test_elion.py
```
