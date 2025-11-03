# System Diagram (FossFLOW Format)

This diagram can be visualized using FossFLOW: https://github.com/stan-smith/FossFLOW

## Component Diagram

```
graph TD
    User[User/Client] --> Examples[Example Scripts]
    User --> CLI[CLI Interface]
    
    Examples --> Portfolio[Portfolio]
    Examples --> Extractor[Data Extractors]
    CLI --> Portfolio
    CLI --> Extractor
    
    Extractor --> YahooFinance[Yahoo Finance Extractor]
    Extractor --> AlphaVantage[Alpha Vantage Extractor]
    Extractor --> BaseExtractor[Base Extractor]
    
    YahooFinance --> PriceSeries[PriceSeries Model]
    AlphaVantage --> PriceSeries
    
    PriceSeries --> Validator[Data Validator]
    PriceSeries --> Cleaner[Data Cleaner]
    
    Validator --> CleanedSeries[Cleaned PriceSeries]
    Cleaner --> CleanedSeries
    
    CleanedSeries --> Portfolio
    
    Portfolio --> MonteCarlo[Monte Carlo Simulation]
    Portfolio --> Statistics[Statistical Analysis]
    Portfolio --> Reporter[Markdown Reporter]
    Portfolio --> Plotter[Plot Generator]
    
    Reporter --> MarkdownFile[Markdown Report]
    Plotter --> PNGFiles[PNG Visualizations]
    
    MonteCarlo --> Results[Simulation Results]
    Results --> Reporter
    Results --> Plotter
```

## Data Flow Diagram

```
sequenceDiagram
    participant User
    participant Extractor
    participant API
    participant PriceSeries
    participant Cleaner
    participant Portfolio
    participant Reporter
    
    User->>Extractor: Request data for symbols
    Extractor->>API: Fetch historical prices
    API-->>Extractor: Raw data
    Extractor->>PriceSeries: Create standardized object
    PriceSeries->>Cleaner: Validate and clean
    Cleaner-->>PriceSeries: Cleaned data
    User->>Portfolio: Create with PriceSeries + holdings
    Portfolio->>Portfolio: Calculate statistics
    User->>Portfolio: Request report
    Portfolio->>Reporter: Generate markdown
    Reporter-->>User: Report file
```

## Class Hierarchy

```
classDiagram
    class BaseExtractor {
        <<abstract>>
        +get_historical_prices()
        +get_index_data()
        +get_multiple_series()
        +search_symbol()
    }
    
    class YahooFinanceExtractor {
        +get_historical_prices()
        +get_index_data()
        +get_crypto_data()
        +get_forex_data()
    }
    
    class PriceSeries {
        +symbol: str
        +data: DataFrame
        +source: str
        +mean_return: float
        +volatility: float
        +sharpe_ratio()
        +annualized_return()
        +resample()
    }
    
    class Portfolio {
        +name: str
        +holdings: Dict
        +price_series: Dict
        +total_value: float
        +monte_carlo_simulation()
        +report()
        +plots_report()
        +get_statistics()
    }
    
    class DataCleaner {
        <<static>>
        +clean_price_series()
        +align_series()
        +resample_to_frequency()
    }
    
    class DataValidator {
        <<static>>
        +validate_price_series()
        +generate_quality_report()
        +can_accept_input()
        +convert_arbitrary_input()
    }
    
    class MarkdownReporter {
        <<static>>
        +generate_portfolio_report()
        +generate_price_series_report()
        +save_report()
    }
    
    class PlotGenerator {
        <<static>>
        +plot_price_history()
        +plot_returns_distribution()
        +plot_portfolio_composition()
        +plot_monte_carlo_simulation()
        +generate_full_report()
    }
    
    BaseExtractor <|-- YahooFinanceExtractor
    YahooFinanceExtractor ..> PriceSeries : creates
    Portfolio *-- PriceSeries : contains
    DataCleaner ..> PriceSeries : processes
    DataValidator ..> PriceSeries : validates
    Portfolio ..> MarkdownReporter : uses
    Portfolio ..> PlotGenerator : uses
```

## Module Dependencies

```
graph LR
    Models[models/] --> Extractors[extractors/]
    Models --> Processors[processors/]
    Models --> Reporting[reporting/]
    
    Extractors --> Utils[utils/]
    Processors --> Utils
    Reporting --> Utils
    
    Examples[examples/] --> Models
    Examples --> Extractors
    Examples --> Processors
    Examples --> Reporting
```

## Deployment Architecture

```
graph TB
    subgraph "User Environment"
        Script[Python Script]
        Jupyter[Jupyter Notebook]
    end
    
    subgraph "Financial Toolkit"
        Core[Core Library]
        Cache[Local Cache]
    end
    
    subgraph "External Services"
        Yahoo[Yahoo Finance API]
        Alpha[Alpha Vantage API]
        Other[Other APIs]
    end
    
    subgraph "Output"
        Reports[Markdown Reports]
        Plots[PNG/PDF Plots]
        Data[CSV/JSON Data]
    end
    
    Script --> Core
    Jupyter --> Core
    Core --> Cache
    Core --> Yahoo
    Core --> Alpha
    Core --> Other
    Core --> Reports
    Core --> Plots
    Core --> Data
```

## Simplified Flow

```
┌─────────────┐
│    USER     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  EXTRACTOR  │────►│ PRICE SERIES │
└─────────────┘     └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PROCESSOR   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PORTFOLIO   │
                    └──────┬───────┘
                           │
                ┌──────────┼──────────┐
                ▼          ▼          ▼
         ┌──────────┐ ┌────────┐ ┌────────┐
         │ ANALYSIS │ │ REPORT │ │  PLOTS │
         └──────────┘ └────────┘ └────────┘
```

## Key Design Patterns

### 1. Strategy Pattern
```
BaseExtractor (Interface)
    ├── YahooFinanceExtractor (Strategy 1)
    ├── AlphaVantageExtractor (Strategy 2)
    └── PolygonExtractor (Strategy 3)
```

### 2. Composition Pattern
```
Portfolio
    ├── PriceSeries (AAPL)
    ├── PriceSeries (GOOGL)
    └── PriceSeries (MSFT)
```

### 3. Factory Pattern
```
DataValidator.convert_arbitrary_input()
    → Creates PriceSeries from any valid DataFrame
```

### 4. Template Method Pattern
```
BaseExtractor.get_multiple_series()
    → Calls get_historical_prices() for each symbol
    → Handles concurrency and error management
```

## Concurrency Model

```
Main Thread
    │
    ├─► ThreadPoolExecutor
    │       ├─► Worker 1: Fetch AAPL
    │       ├─► Worker 2: Fetch GOOGL
    │       ├─► Worker 3: Fetch MSFT
    │       └─► Worker N: Fetch ...
    │
    └─► Collect Results → Create Portfolio
```

## Error Handling Flow

```
API Call
    │
    ├─► Success → Parse → Validate → PriceSeries
    │
    └─► Failure → Log Error → Continue with other symbols
                              │
                              └─► Report failed symbols to user
```

This diagram structure follows software engineering best practices and can be easily maintained as the project evolves.
