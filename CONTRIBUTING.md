# Contributing to Financial Market Analysis Toolkit

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Code samples if applicable

### Suggesting Enhancements

1. Check existing issues and pull requests
2. Create an issue describing:
   - The enhancement and its benefits
   - Possible implementation approach
   - Any potential drawbacks

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Update documentation as needed
6. Commit with clear messages (`git commit -m 'Add some AmazingFeature'`)
7. Push to your branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md for user-facing changes
- Add examples for new features

### Testing

- Write unit tests for new code
- Maintain or improve code coverage
- Test edge cases
- Use pytest for testing

### Example Code Style

```python
def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    trading_days: int = 252
) -> float:
    """
    Calculate the Sharpe ratio for a return series.
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default: 0.02)
        trading_days: Trading days per year (default: 252)
    
    Returns:
        Sharpe ratio as a float
    
    Raises:
        ValueError: If returns series is empty
    """
    if len(returns) == 0:
        raise ValueError("Returns series cannot be empty")
    
    ann_return = (1 + returns.mean()) ** trading_days - 1
    ann_vol = returns.std() * np.sqrt(trading_days)
    
    return (ann_return - risk_free_rate) / ann_vol if ann_vol != 0 else 0.0
```

## Project Structure

When adding new features, follow the existing structure:

```
src/
├── models/          # Domain objects
├── extractors/      # Data acquisition
├── processors/      # Data processing
├── analytics/       # Analysis algorithms
├── reporting/       # Output generation
└── utils/           # Utilities
```

## Commit Messages

Use clear, descriptive commit messages:

- `feat: Add support for cryptocurrency data`
- `fix: Correct calculation of annualized volatility`
- `docs: Update README with new examples`
- `test: Add tests for Portfolio class`
- `refactor: Simplify data cleaning logic`

## Questions?

Feel free to open an issue for any questions about contributing!
