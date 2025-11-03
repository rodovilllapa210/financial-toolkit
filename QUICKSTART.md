# 🚀 Quick Start Guide

Guía rápida para empezar a usar el Financial Market Analysis Toolkit en 5 minutos.

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalar Dependencias (2 min)

```bash
pip install -r requirements.txt
```

### 2. Ejecutar Test Comprehensivo (3 min)

```bash
python examples/comprehensive_test.py
```

Este script:
- ✅ Descarga datos de 3 fuentes (Yahoo, Stooq, Alpha Vantage*)
- ✅ Prueba acciones, índices, crypto y bonos
- ✅ Valida y limpia datos
- ✅ Crea una cartera
- ✅ Ejecuta simulación Monte Carlo
- ✅ Genera reportes (Markdown + gráficos)

**Salida**: `reports/comprehensive_test_report.md` y `reports/plots/*.png`

*Alpha Vantage requiere API key (opcional)

---

## 📝 Ejemplo Básico (Copy-Paste)

```python
from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.extractors.stooq import StooqExtractor
from src.models.portfolio import Portfolio
from datetime import datetime, timedelta

# Configurar fechas
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# 1. Descargar datos
yahoo = YahooFinanceExtractor()
stooq = StooqExtractor()

# Acciones
aapl = yahoo.get_historical_prices("AAPL", start_date, end_date)
msft = yahoo.get_historical_prices("MSFT", start_date, end_date)

# Índice
sp500 = yahoo.get_index_data("^GSPC", start_date, end_date)

# Crypto
btc = yahoo.get_crypto_data("BTC-USD", start_date, end_date)

# Bono (¡nuevo!)
bond = stooq.get_bond_data("10USY.B", start_date, end_date)

# 2. Crear cartera
portfolio = Portfolio(
    name="Mi Cartera",
    holdings={
        "AAPL": 100,
        "MSFT": 50,
        "BTC-USD": 2,
        "10USY.B": 1000
    },
    price_series={
        "AAPL": aapl,
        "MSFT": msft,
        "BTC-USD": btc,
        "10USY.B": bond
    }
)

# 3. Análisis
print(f"Valor total: ${portfolio.total_value:,.2f}")
print(f"Retorno: {portfolio.total_return():.2%}")
print(f"Sharpe: {portfolio.portfolio_sharpe():.3f}")

# 4. Monte Carlo
mc_results = portfolio.monte_carlo_simulation(n_simulations=1000, n_days=252)
print(f"Valor esperado (1 año): ${mc_results['mean_final_value']:,.2f}")

# 5. Reportes
portfolio.report(output_file="mi_cartera.md", include_monte_carlo=True)
portfolio.plots_report(output_dir="./mis_graficos")

print("✅ ¡Listo! Revisa mi_cartera.md y ./mis_graficos/")
```

---

## 🧪 Verificar que Todo Funciona

### Opción 1: Test Comprehensivo (Recomendado)
```bash
python examples/comprehensive_test.py
```

### Opción 2: Tests Unitarios
```bash
python -m pytest tests/ -v
```

### Opción 3: Test Rápido
```bash
python -m pytest tests/test_price_series.py::test_price_series_creation -v
```

Si alguno de estos funciona, ¡estás listo! ✅

---

## 📚 Fuentes de Datos Disponibles

### Yahoo Finance (Gratis, No API Key)
```python
from src.extractors.yahoo_finance import YahooFinanceExtractor

yahoo = YahooFinanceExtractor()

# Acciones
aapl = yahoo.get_historical_prices("AAPL", start_date, end_date)

# Índices
sp500 = yahoo.get_index_data("^GSPC", start_date, end_date)

# Crypto
btc = yahoo.get_crypto_data("BTC-USD", start_date, end_date)

# Forex
eurusd = yahoo.get_forex_data("EUR", "USD", start_date, end_date)

# Múltiples símbolos (concurrente)
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
data = yahoo.get_multiple_series(symbols, start_date, end_date)
```

### Stooq (Gratis, No API Key)
```python
from src.extractors.stooq import StooqExtractor

stooq = StooqExtractor()

# Acciones US
aapl = stooq.get_us_stock_data("AAPL", start_date, end_date)

# Índices
sp500 = stooq.get_index_data("^SPX", start_date, end_date)

# Bonos (¡excelente cobertura!)
bond_10y = stooq.get_bond_data("10USY.B", start_date, end_date)
bond_2y = stooq.get_bond_data("2USY.B", start_date, end_date)

# Crypto
btc = stooq.get_crypto_data("BTC", start_date, end_date)
```

### Alpha Vantage (Gratis con API Key)
```python
from src.extractors.alpha_vantage import AlphaVantageExtractor
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

alpha = AlphaVantageExtractor(api_key=api_key)

# Usar igual que los otros extractores
aapl = alpha.get_historical_prices("AAPL", start_date, end_date)
```

**Obtener API Key**: https://www.alphavantage.co/support/#api-key

---

## 🔧 Validación y Limpieza de Datos

```python
from src.processors.data_cleaner import DataCleaner
from src.processors.data_validator import DataValidator

# 1. Generar reporte de calidad
quality = DataValidator.generate_quality_report(aapl.data)
print(f"Quality Score: {quality['quality_score']:.1f}%")
print(f"Missing Values: {quality['missing_values']}")
print(f"Outliers: {quality['outliers']}")

# 2. Limpiar datos
cleaned = DataCleaner.handle_missing_values(aapl.data, method='interpolate')
cleaned = DataCleaner.clip_outliers(cleaned, column='close', method='iqr')

# 3. Detectar outliers
outliers = DataCleaner.detect_outliers(aapl.data, column='close', method='iqr')
print(f"Outliers detectados: {outliers.sum()}")
```

---

## 📊 Análisis Estadístico

```python
# PriceSeries
print(f"Mean: ${aapl.mean:.2f}")
print(f"Std Dev: ${aapl.std:.2f}")
print(f"Sharpe Ratio: {aapl.sharpe_ratio():.3f}")
print(f"Volatility: {aapl.volatility():.2%}")
print(f"Max Drawdown: {aapl.max_drawdown():.2%}")

# Portfolio
print(f"Total Value: ${portfolio.total_value:,.2f}")
print(f"Total Return: {portfolio.total_return():.2%}")
print(f"Portfolio Sharpe: {portfolio.portfolio_sharpe():.3f}")
print(f"Best Performer: {portfolio.best_performer()}")
print(f"Worst Performer: {portfolio.worst_performer()}")

# Correlaciones
corr_matrix = portfolio.correlation_matrix()
print(corr_matrix)
```

---

## 🎲 Simulación Monte Carlo

```python
# Simulación básica
results = portfolio.monte_carlo_simulation(
    n_simulations=1000,
    n_days=252,  # 1 año
    method='gbm'  # Geometric Brownian Motion
)

print(f"Mean Final Value: ${results['mean_final_value']:,.2f}")
print(f"Median Final Value: ${results['median_final_value']:,.2f}")
print(f"5th Percentile: ${results['percentile_5']:,.2f}")
print(f"95th Percentile: ${results['percentile_95']:,.2f}")
print(f"Probability of Loss: {results['probability_of_loss']:.2%}")

# Simulación con parámetros personalizados
results = portfolio.monte_carlo_simulation(
    n_simulations=5000,
    n_days=504,  # 2 años
    method='historical'  # Bootstrap histórico
)
```

---

## 📝 Generación de Reportes

```python
# Reporte Markdown
report = portfolio.report(
    output_file="mi_reporte.md",
    include_monte_carlo=True,
    include_correlations=True,
    monte_carlo_params={'n_simulations': 1000, 'n_days': 252},
    print_to_console=True
)

# Gráficos
portfolio.plots_report(
    output_dir="./graficos",
    include_monte_carlo=True,
    monte_carlo_params={'n_simulations': 1000, 'n_days': 252}
)

# Gráficos generados:
# - portfolio_value.png
# - returns_distribution.png
# - correlation_matrix.png
# - monte_carlo_simulation.png
# - composition_pie.png
# - cumulative_returns.png
# - volatility_comparison.png
```

---

## 🎯 Casos de Uso Comunes

### 1. Análisis de una Acción
```python
yahoo = YahooFinanceExtractor()
aapl = yahoo.get_historical_prices("AAPL", start_date, end_date)

print(f"Sharpe: {aapl.sharpe_ratio():.3f}")
print(f"Volatility: {aapl.volatility():.2%}")
print(f"Max Drawdown: {aapl.max_drawdown():.2%}")
```

### 2. Comparar Múltiples Acciones
```python
symbols = ["AAPL", "MSFT", "GOOGL"]
data = yahoo.get_multiple_series(symbols, start_date, end_date)

for symbol, series in data.items():
    print(f"{symbol}: Sharpe={series.sharpe_ratio():.3f}")
```

### 3. Cartera Diversificada
```python
portfolio = Portfolio(
    name="Diversificada",
    holdings={"AAPL": 100, "^GSPC": 10, "BTC-USD": 1, "10USY.B": 1000},
    price_series={...}
)

print(portfolio.get_composition())
print(portfolio.correlation_matrix())
```

### 4. Análisis de Bonos
```python
stooq = StooqExtractor()
bond_10y = stooq.get_bond_data("10USY.B", start_date, end_date)
bond_2y = stooq.get_bond_data("2USY.B", start_date, end_date)

print(f"10Y Mean: {bond_10y.mean:.3f}%")
print(f"2Y Mean: {bond_2y.mean:.3f}%")
print(f"Spread: {bond_10y.mean - bond_2y.mean:.3f}%")
```

### 5. Crypto Portfolio
```python
crypto_portfolio = Portfolio(
    name="Crypto",
    holdings={"BTC-USD": 1, "ETH-USD": 10},
    price_series={...}
)

print(f"Volatility: {crypto_portfolio.portfolio_volatility():.2%}")
```

---

## ❓ Solución Rápida de Problemas

### Error: "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Error: "No data returned"
```python
# Verificar símbolo
yahoo.validate_symbol("AAPL")  # True si válido

# Usar fallback
try:
    data = yahoo.get_historical_prices(symbol, start, end)
except:
    data = stooq.get_us_stock_data(symbol, start, end)
```

### Error: "OHLC validation failed"
```python
from src.processors.data_cleaner import DataCleaner

cleaned = DataCleaner.handle_missing_values(data)
cleaned = DataCleaner.clip_outliers(cleaned, column='close')
```

---

## 📖 Documentación Completa

- **README.md**: Documentación principal
- **DATA_SOURCES.md**: Guía de fuentes de datos
- **TESTING_GUIDE.md**: Guía de testing
- **IMPLEMENTATION_SUMMARY.md**: Resumen de implementación
- **examples/**: Ejemplos de uso
- **docs/**: Documentación adicional

---

## 🚀 Próximos Pasos

1. ✅ Ejecuta `python examples/comprehensive_test.py`
2. ✅ Revisa los reportes generados en `reports/`
3. ✅ Prueba el ejemplo básico de arriba
4. ✅ Lee `DATA_SOURCES.md` para más detalles
5. ✅ Explora los ejemplos en `examples/`
6. ✅ Ejecuta los tests: `python -m pytest tests/ -v`

---

## 💡 Tips

- **Usa Yahoo Finance** para empezar (gratis, no requiere API key)
- **Usa Stooq** para bonos (mejor cobertura)
- **Descarga concurrente** para múltiples símbolos
- **Valida datos** antes de análisis importantes
- **Genera reportes** para documentar análisis

---

¡Listo para empezar! 🎉

Para más ayuda, consulta la documentación completa o abre un issue en GitHub.
