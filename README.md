# Financial Market Analysis Toolkit

## 📊 Descripción

Sistema profesional de análisis bursátil diseñado con arquitectura limpia y buenas prácticas de ingeniería de software. Permite la extracción, procesamiento, análisis y visualización de datos financieros desde múltiples fuentes.

## 🎯 Características Principales

- **Extracción Multi-Fuente**: Obtención de datos desde múltiples APIs (Yahoo Finance, Alpha Vantage, Stooq)
- **Estandarización de Datos**: Formato unificado independientemente de la fuente
- **Múltiples Tipos de Activos**: Acciones, índices, criptomonedas, bonos, forex
- **DataClasses Robustas**: Modelos de datos para series de precios y carteras
- **Análisis Estadístico**: Cálculos automáticos de métricas relevantes
- **Simulación Monte Carlo**: Proyecciones de evolución de carteras
- **Limpieza de Datos**: Preprocesado automático y validación
- **Reporting Avanzado**: Generación de informes en Markdown y visualizaciones
- **Procesamiento Concurrente**: Descarga paralela de múltiples series

## 🏗️ Arquitectura

```
financial-toolkit/
├── src/
│   ├── __init__.py
│   ├── models/              # DataClasses y modelos de dominio
│   │   ├── __init__.py
│   │   ├── price_series.py  # Serie temporal de precios
│   │   └── portfolio.py     # Cartera de activos
│   ├── extractors/          # Extractores de datos
│   │   ├── __init__.py
│   │   ├── base.py          # Clase base abstracta
│   │   ├── yahoo_finance.py # Yahoo Finance (gratis)
│   │   ├── alpha_vantage.py # Alpha Vantage (API key)
│   │   └── stooq.py         # Stooq (gratis)
│   ├── processors/          # Procesamiento y limpieza
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   └── validator.py
│   ├── analytics/           # Análisis y simulaciones
│   │   ├── __init__.py
│   │   ├── statistics.py
│   │   └── monte_carlo.py
│   ├── reporting/           # Generación de informes
│   │   ├── __init__.py
│   │   ├── markdown_report.py
│   │   └── plots.py
│   └── utils/               # Utilidades
│       ├── __init__.py
│       └── helpers.py
├── tests/                   # Tests unitarios
├── examples/                # Ejemplos de uso
├── docs/                    # Documentación adicional
├── requirements.txt
├── setup.py
├── .gitignore
└── README.md
```

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- pip

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/financial-toolkit.git
cd financial-toolkit

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .
```

## 📖 Uso Básico

### Extracción de Datos

```python
from src.extractors.yahoo_finance import YahooFinanceExtractor
from datetime import datetime, timedelta

# Crear extractor
extractor = YahooFinanceExtractor()

# Obtener datos históricos de una acción
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

apple_data = extractor.get_historical_prices(
    symbol="AAPL",
    start_date=start_date,
    end_date=end_date
)

# Obtener múltiples series simultáneamente
symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
multiple_data = extractor.get_multiple_series(symbols, start_date, end_date)
```

### Creación de Cartera

```python
from src.models.portfolio import Portfolio

# Crear cartera desde series de precios
portfolio = Portfolio(
    name="Tech Portfolio",
    holdings={
        "AAPL": 10,    # 10 acciones de Apple
        "GOOGL": 5,    # 5 acciones de Google
        "MSFT": 15     # 15 acciones de Microsoft
    },
    price_series=multiple_data
)

# Obtener estadísticas automáticas
print(f"Valor total: ${portfolio.total_value:,.2f}")
print(f"Retorno medio: {portfolio.mean_return:.2%}")
print(f"Volatilidad: {portfolio.volatility:.2%}")
```

### Simulación Monte Carlo

```python
# Simular evolución de la cartera
simulation_results = portfolio.monte_carlo_simulation(
    n_simulations=10000,
    n_days=252,  # 1 año de trading
    confidence_level=0.95
)

# Visualizar resultados
portfolio.plot_monte_carlo(simulation_results)
```

### Generación de Informes

```python
# Generar informe en Markdown
portfolio.report(
    output_file="portfolio_analysis.md",
    include_monte_carlo=True,
    include_correlations=True
)

# Generar visualizaciones
portfolio.plots_report(output_dir="./reports/plots")
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
POLYGON_API_KEY=tu_api_key_aqui
```

## 📊 Tipos de Datos Soportados

- **Precios Históricos**: Acciones, índices, ETFs
- **Datos Fundamentales**: Ratios financieros, balances
- **Datos Macroeconómicos**: Tipos de interés, inflación
- **Criptomonedas**: Precios y volúmenes

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest --cov=src tests/
```

## 📈 Ejemplos Avanzados

Ver la carpeta `examples/` para casos de uso detallados:

- `01_basic_extraction.py`: Extracción básica de datos
- `02_portfolio_creation.py`: Creación y análisis de carteras
- `03_monte_carlo.py`: Simulaciones avanzadas
- `04_custom_reports.py`: Informes personalizados
- `comprehensive_test.py`: **Test completo de todas las funcionalidades**

### Ejecutar el Test Comprehensivo

```bash
python examples/comprehensive_test.py
```

Este script prueba:
- ✅ Extracción de datos de 3 fuentes (Yahoo Finance, Alpha Vantage, Stooq)
- ✅ Descarga de acciones, índices, criptomonedas y bonos
- ✅ Validación y limpieza de datos
- ✅ Manejo de valores faltantes y outliers
- ✅ Creación de carteras y análisis
- ✅ Simulación Monte Carlo
- ✅ Generación de informes (Markdown y gráficos)

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- Tu Nombre - Proyecto MIAX

## 🙏 Agradecimientos

- Yahoo Finance API
- Alpha Vantage
- Stooq
- Comunidad de Python Finance

## 📞 Contacto

Para preguntas o sugerencias, abre un issue en GitHub.
