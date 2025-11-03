# Architecture Documentation

## Overview

This document describes the architecture of the Financial Market Analysis Toolkit, a professional-grade system for extracting, processing, and analyzing financial market data.

## Design Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- **Extractors**: Data acquisition from external sources
- **Models**: Domain objects and business logic
- **Processors**: Data cleaning and validation
- **Analytics**: Statistical analysis and simulations
- **Reporting**: Output generation and visualization

### 2. **Abstraction and Polymorphism**
- `BaseExtractor` defines a common interface for all data sources
- Any new data source can be added by implementing the base interface
- Output is always standardized to `PriceSeries` objects

### 3. **Data Standardization**
Regardless of the source API, all data is converted to a unified format:
```python
PriceSeries(
    symbol, name, data, source, asset_type, currency, metadata
)
```

### 4. **Composition Over Inheritance**
- `Portfolio` is composed of `PriceSeries` objects
- Methods are added to classes rather than creating deep inheritance hierarchies

### 5. **Immutability Where Possible**
- DataClasses with calculated properties
- Operations return new objects rather than modifying in place

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Examples, Scripts, CLI)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REPORTING LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │ MarkdownReporter │              │  PlotGenerator   │        │
│  │  - report()      │              │  - plot_*()      │        │
│  │  - save_report() │              │  - generate_*()  │        │
│  └──────────────────┘              └──────────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DOMAIN MODELS                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   PriceSeries    │◄─────────────│    Portfolio     │        │
│  │  - data          │  contains N  │  - holdings      │        │
│  │  - statistics    │              │  - monte_carlo() │        │
│  │  - methods       │              │  - report()      │        │
│  └──────────────────┘              └──────────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   DataCleaner    │              │  DataValidator   │        │
│  │  - clean()       │              │  - validate()    │        │
│  │  - align()       │              │  - quality_rep() │        │
│  │  - resample()    │              │  - convert()     │        │
│  └──────────────────┘              └──────────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                  ┌──────────────────┐                           │
│                  │  BaseExtractor   │                           │
│                  │   (Abstract)     │                           │
│                  └────────┬─────────┘                           │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         ▼                 ▼                 ▼                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Yahoo     │  │    Alpha    │  │   Future    │           │
│  │  Finance    │  │   Vantage   │  │  Extractors │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                       │
│         (Yahoo Finance, Alpha Vantage, Polygon, etc.)           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Extraction
```
User Request → Extractor → API Call → Raw Data → PriceSeries
```

### 2. Data Processing
```
PriceSeries → Validator → Cleaner → Clean PriceSeries
```

### 3. Portfolio Creation
```
Multiple PriceSeries + Holdings → Portfolio → Statistics
```

### 4. Analysis
```
Portfolio → Monte Carlo → Simulation Results → Visualization
```

### 5. Reporting
```
Portfolio → Reporter → Markdown/Plots → Output Files
```

## Class Relationships

### PriceSeries
**Purpose**: Standardized representation of a financial time series

**Key Attributes**:
- `symbol`: Ticker symbol
- `data`: DataFrame with OHLCV data
- `source`: Origin of the data

**Key Methods**:
- Statistics: `mean_return`, `volatility`, `sharpe_ratio`
- Transformations: `resample()`, `to_dict()`

**Automatic Calculations**:
- Mean and std deviation computed on initialization
- Returns calculated automatically

### Portfolio
**Purpose**: Collection of PriceSeries with quantities

**Composition**: `Portfolio` HAS-A collection of `PriceSeries`

**Key Methods**:
- `monte_carlo_simulation()`: Risk analysis
- `report()`: Generate Markdown report
- `plots_report()`: Generate visualizations
- `get_statistics()`: Portfolio-level metrics

**Philosophy**: A portfolio is essentially a weighted combination of price series

### BaseExtractor (Abstract)
**Purpose**: Define interface for all data extractors

**Key Methods** (must implement):
- `get_historical_prices()`
- `get_index_data()`
- `search_symbol()`

**Built-in Features**:
- Concurrent downloads via `get_multiple_series()`
- Progress tracking
- Error handling

### DataCleaner
**Purpose**: Preprocess and clean financial data

**Key Methods**:
- `clean_price_series()`: Handle missing values, outliers
- `align_series()`: Synchronize multiple series
- `resample_to_frequency()`: Change time frequency

**Philosophy**: Accept any reasonable input, make it usable

### DataValidator
**Purpose**: Validate data quality and convert arbitrary inputs

**Key Methods**:
- `validate_price_series()`: Check data quality
- `generate_quality_report()`: Comprehensive analysis
- `can_accept_input()`: Check if data is convertible
- `convert_arbitrary_input()`: Convert any DataFrame to PriceSeries

**Philosophy**: Be flexible with inputs, strict with outputs

## Extension Points

### Adding a New Data Source

1. Create new extractor class inheriting from `BaseExtractor`
2. Implement required abstract methods
3. Convert output to `PriceSeries` format
4. Register in `__init__.py`

Example:
```python
class AlphaVantageExtractor(BaseExtractor):
    def get_historical_prices(self, symbol, start_date, end_date):
        # Fetch from Alpha Vantage API
        raw_data = self._fetch_from_api(symbol)
        
        # Convert to standard format
        df = self._convert_to_standard_format(raw_data)
        
        # Return PriceSeries
        return PriceSeries(
            symbol=symbol,
            data=df,
            source='alpha_vantage',
            ...
        )
```

### Adding New Analysis Methods

Add methods to `Portfolio` or `PriceSeries` classes:

```python
# In Portfolio class
def calculate_var(self, confidence_level=0.95):
    """Calculate Value at Risk"""
    returns = self.get_portfolio_returns()
    return np.percentile(returns, (1 - confidence_level) * 100)
```

### Adding New Visualizations

Add static methods to `PlotGenerator`:

```python
@staticmethod
def plot_drawdown_analysis(portfolio, save_path=None):
    """Plot drawdown over time"""
    # Implementation
    pass
```

## Concurrency and Performance

### Concurrent Downloads
- Uses `ThreadPoolExecutor` for parallel API calls
- Configurable `max_workers` parameter
- Progress tracking with `tqdm`

### Caching Strategy
- Consider implementing caching for frequently accessed data
- Use pickle or HDF5 for serialization

### Memory Management
- Large DataFrames are not copied unnecessarily
- Use views where possible
- Clean up after plot generation

## Error Handling

### Extraction Errors
- Individual failures don't stop batch operations
- Failed symbols are logged and reported
- Graceful degradation

### Validation Errors
- Clear error messages with actionable information
- Warnings vs. errors distinction
- Quality scores for data assessment

### Processing Errors
- Validation before processing
- Fallback strategies (e.g., forward fill for missing data)
- User control over strictness

## Testing Strategy

### Unit Tests
- Test each class in isolation
- Mock external API calls
- Test edge cases

### Integration Tests
- Test complete workflows
- Use cached sample data
- Verify output formats

### Example Tests
```python
def test_price_series_creation():
    df = create_sample_data()
    ps = PriceSeries(symbol="TEST", data=df, ...)
    assert ps.mean_return is not None
    assert len(ps) == len(df)
```

## Future Enhancements

1. **Additional Data Sources**
   - Polygon.io
   - IEX Cloud
   - Quandl

2. **Advanced Analytics**
   - Factor analysis
   - Optimization algorithms
   - Machine learning integration

3. **Real-time Data**
   - WebSocket connections
   - Streaming data processing

4. **Database Integration**
   - PostgreSQL for historical data
   - Redis for caching

5. **Web Interface**
   - Flask/FastAPI backend
   - React frontend
   - Interactive dashboards

## Conclusion

This architecture prioritizes:
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new features
- **Reliability**: Robust error handling
- **Usability**: Intuitive interfaces

The design allows the project to grow from a simple script to a production-grade system while maintaining code quality and developer experience.
