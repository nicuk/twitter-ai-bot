# Legacy Components

This directory contains components that were part of the original Elion project but have been moved aside during the streamlining process. These components are preserved for reference and potential future integration.

## Directory Structure

### elion_components/
Components that were originally part of the Elion package but are now handled by other modules:
- `content/` - Content generation (now handled by strategies)
- `data_sources/` - Data fetching (now handled by strategies/shared_utils.py)
- `utils/` - Utilities (now in strategies/shared_utils.py)
- `engagement/` - Engagement system (now handled by personality/traits.py)
- `personality.py` - Root level personality (now in personality/traits.py)

### root_level/
Old versions of root-level files that have been replaced or integrated:
- `twitter_api_bot.py` - (now in twitter/ module)
- `twitter_bot.py` - (now in twitter/ module)
- `old_manager.py` - (old version)
- `new_manager.py` - (old version)

### future_features/
Components planned for future integration:
- `portfolio/` - Portfolio management system (to be integrated later)

## Note
These components are preserved to:
1. Maintain a reference of the original implementation
2. Allow for easy restoration if needed
3. Preserve functionality that might be useful in future iterations
