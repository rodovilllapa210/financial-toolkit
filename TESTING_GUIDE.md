# Guía de Testing

Esta guía explica cómo probar todas las funcionalidades del Financial Market Analysis Toolkit.

## 📋 Tabla de Contenidos

1. [Instalación de Dependencias](#instalación-de-dependencias)
2. [Tests Unitarios](#tests-unitarios)
3. [Test Comprehensivo](#test-comprehensivo)
4. [Verificación de Funcionalidades](#verificación-de-funcionalidades)
5. [Solución de Problemas](#solución-de-problemas)

---

## 🔧 Instalación de Dependencias

### Paso 1: Instalar todas las dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- **Core**: numpy, pandas, scipy
- **Data extraction**: yfinance, pandas-datareader, requests
- **Visualization**: matplotlib, seaborn, plotly
- **Testing**: pytest, pytest-cov
- **Development**: black, flake8, mypy
- **Utilities**: loguru, tqdm, python-dotenv

### Paso 2: Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu API key de Alpha Vantage
# ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
```

**Obtener API Key de Alpha Vantage** (opcional, pero recomendado):
1. Visita: https://www.alphavantage.co/support/#api-key
2. Registra tu email
3. Copia tu API key
4. Añádela al archivo `.env`

---

## 🧪 Tests Unitarios

### Ejecutar todos los tests

```bash
python -m pytest tests/ -v
```

### Ejecutar tests específicos

#### Tests de PriceSeries
```bash
python -m pytest tests/test_price_series.py -v
```

Tests incluidos:
- ✅ Creación de PriceSeries
- ✅ Validación de datos
- ✅ Cálculos estadísticos (mean, std, Sharpe ratio)
- ✅ Retornos y volatilidad
- ✅ Max drawdown
- ✅ Resampling
- ✅ Manejo de errores

#### Tests de Portfolio
```bash
python -m pytest tests/test_portfolio.py -v
```

Tests incluidos:
- ✅ Creación de carteras
- ✅ Composición y pesos
- ✅ Estadísticas de cartera
- ✅ Correlaciones
- ✅ Simulación Monte Carlo
- ✅ Best/worst performers

#### Tests de Extractors
```bash
python -m pytest tests/test_extractors.py -v
```

Tests incluidos:
- ✅ Yahoo Finance: acciones, índices, crypto, forex
- ✅ Stooq: acciones, índices, bonos, crypto
- ✅ Descarga concurrente
- ✅ Estandarización de datos
- ✅ Correlación entre fuentes
- ✅ Manejo de errores

#### Tests de Data Processing
```bash
python -m pytest tests/test_data_processing.py -v
```

Tests incluidos:
- ✅ Manejo de valores faltantes (ffill, bfill, interpolate, drop)
- ✅ Detección de outliers (IQR, Z-score)
- ✅ Eliminación y clipping de outliers
- ✅ Relleno de gaps de fechas
- ✅ Validación OHLC
- ✅ Validación de precios positivos
- ✅ Reportes de calidad de datos
- ✅ Conversión de formatos arbitrarios

### Ejecutar tests con cobertura

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

Esto generará un reporte de cobertura en `htmlcov/index.html`.

### Ejecutar tests marcados como lentos

Algunos tests pueden tardar más (ej: descargas de datos):

```bash
# Ejecutar solo tests rápidos
python -m pytest tests/ -v -m "not slow"

# Ejecutar todos incluyendo lentos
python -m pytest tests/ -v
```

---

## 🎯 Test Comprehensivo

El test comprehensivo verifica **TODAS** las funcionalidades del toolkit en un solo script.

### Ejecutar el test comprehensivo

```bash
python examples/comprehensive_test.py
```

### ¿Qué prueba?

#### 1. Extracción de Datos - Yahoo Finance
- ✅ Descarga de acciones (AAPL)
- ✅ Descarga de índices (S&P 500)
- ✅ Descarga de criptomonedas (Bitcoin)
- ✅ Descarga concurrente de múltiples símbolos

#### 2. Extracción de Datos - Stooq
- ✅ Descarga de acciones US (AAPL.US)
- ✅ Descarga de índices (^SPX)
- ✅ Descarga de bonos (10-year US Treasury)
- ✅ Descarga de criptomonedas (BTC.USD)

#### 3. Validación y Limpieza de Datos
- ✅ Generación de reportes de calidad
- ✅ Manejo de valores faltantes
- ✅ Detección de outliers (IQR y Z-score)
- ✅ Validación OHLC

#### 4. Creación y Análisis de Carteras
- ✅ Creación de cartera diversificada
- ✅ Análisis de composición
- ✅ Matriz de correlaciones
- ✅ Estadísticas de cartera

#### 5. Simulación Monte Carlo
- ✅ Simulación con método GBM
- ✅ Cálculo de percentiles
- ✅ Probabilidad de pérdida
- ✅ Proyecciones de valor

#### 6. Generación de Informes
- ✅ Reporte Markdown completo
- ✅ Generación de gráficos
- ✅ Visualizaciones múltiples

#### 7. Métodos Estadísticos
- ✅ Estadísticas de PriceSeries
- ✅ Estadísticas de Portfolio
- ✅ Retornos y volatilidad
- ✅ Sharpe ratio y max drawdown

### Salida esperada

El script genera:
```
reports/
├── comprehensive_test_report.md    # Reporte completo en Markdown
└── plots/                          # Carpeta con gráficos
    ├── portfolio_value.png
    ├── returns_distribution.png
    ├── correlation_matrix.png
    ├── monte_carlo_simulation.png
    └── ...
```

---

## ✅ Verificación de Funcionalidades

### Checklist de Funcionalidades

Usa este checklist para verificar que todo funciona:

#### Extracción de Datos
- [ ] Yahoo Finance descarga acciones correctamente
- [ ] Yahoo Finance descarga índices correctamente
- [ ] Yahoo Finance descarga criptomonedas correctamente
- [ ] Stooq descarga acciones correctamente
- [ ] Stooq descarga índices correctamente
- [ ] Stooq descarga bonos correctamente
- [ ] Descarga concurrente funciona
- [ ] Datos están estandarizados (mismo formato)

#### Validación y Limpieza
- [ ] Detecta valores faltantes
- [ ] Maneja valores faltantes (ffill, bfill, interpolate)
- [ ] Detecta outliers (IQR)
- [ ] Detecta outliers (Z-score)
- [ ] Valida OHLC correctamente
- [ ] Genera reportes de calidad
- [ ] Rellena gaps de fechas

#### Análisis de Series
- [ ] Calcula media y desviación estándar
- [ ] Calcula retornos
- [ ] Calcula retornos acumulados
- [ ] Calcula volatilidad
- [ ] Calcula Sharpe ratio
- [ ] Calcula max drawdown

#### Análisis de Carteras
- [ ] Crea carteras correctamente
- [ ] Calcula composición
- [ ] Calcula correlaciones
- [ ] Calcula estadísticas de cartera
- [ ] Identifica best/worst performers

#### Simulación Monte Carlo
- [ ] Ejecuta simulación GBM
- [ ] Calcula percentiles
- [ ] Calcula probabilidad de pérdida
- [ ] Genera proyecciones

#### Reporting
- [ ] Genera reportes Markdown
- [ ] Genera gráficos
- [ ] Guarda archivos correctamente

---

## 🐛 Solución de Problemas

### Error: "No module named 'loguru'"

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "No module named 'pytest'"

**Solución**:
```bash
pip install pytest pytest-cov
```

### Error: "No data returned for symbol"

**Causas posibles**:
1. Símbolo incorrecto
2. Sin conexión a internet
3. API temporalmente no disponible
4. Rate limiting

**Solución**:
```python
# Verificar símbolo
extractor.validate_symbol("AAPL")  # True si es válido

# Usar fallback entre fuentes
try:
    data = yahoo_extractor.get_historical_prices(symbol, start, end)
except:
    data = stooq_extractor.get_us_stock_data(symbol, start, end)
```

### Error: "Alpha Vantage API key required"

**Solución**:
1. Obtén una API key gratis: https://www.alphavantage.co/support/#api-key
2. Añádela al archivo `.env`:
   ```
   ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
   ```

### Tests fallan por timeout

**Solución**:
```bash
# Ejecutar solo tests rápidos
python -m pytest tests/ -v -m "not slow"

# O aumentar el timeout
python -m pytest tests/ -v --timeout=300
```

### Error: "OHLC validation failed"

**Causa**: Los datos tienen relaciones OHLC inválidas (ej: high < low)

**Solución**:
```python
from src.processors.data_cleaner import DataCleaner

# Limpiar datos antes de crear PriceSeries
cleaned_data = DataCleaner.handle_missing_values(data)
cleaned_data = DataCleaner.clip_outliers(cleaned_data, column='close')
```

### Gráficos no se generan

**Causas posibles**:
1. Directorio de salida no existe
2. Permisos insuficientes
3. Matplotlib no configurado correctamente

**Solución**:
```python
import os
os.makedirs("./reports/plots", exist_ok=True)

# Verificar que matplotlib funciona
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
plt.savefig("test.png")
```

---

## 📊 Ejemplos de Comandos Útiles

### Ejecutar tests específicos por nombre

```bash
# Test específico
python -m pytest tests/test_price_series.py::test_sharpe_ratio -v

# Tests que contienen "outlier"
python -m pytest tests/ -k "outlier" -v

# Tests que NO contienen "slow"
python -m pytest tests/ -k "not slow" -v
```

### Generar reporte de cobertura

```bash
# HTML
python -m pytest tests/ --cov=src --cov-report=html

# Terminal
python -m pytest tests/ --cov=src --cov-report=term

# XML (para CI/CD)
python -m pytest tests/ --cov=src --cov-report=xml
```

### Ejecutar tests en paralelo (requiere pytest-xdist)

```bash
pip install pytest-xdist
python -m pytest tests/ -n auto
```

### Ver output detallado

```bash
# Mostrar prints
python -m pytest tests/ -v -s

# Mostrar warnings
python -m pytest tests/ -v -W all

# Modo verbose máximo
python -m pytest tests/ -vv
```

---

## 🎓 Mejores Prácticas

1. **Ejecuta tests antes de commit**:
   ```bash
   python -m pytest tests/ -v
   ```

2. **Verifica cobertura regularmente**:
   ```bash
   python -m pytest tests/ --cov=src --cov-report=term
   ```

3. **Ejecuta el test comprehensivo antes de releases**:
   ```bash
   python examples/comprehensive_test.py
   ```

4. **Mantén los tests rápidos**:
   - Usa fixtures para datos de prueba
   - Marca tests lentos con `@pytest.mark.slow`
   - Usa mocks para APIs externas cuando sea posible

5. **Documenta tests nuevos**:
   - Añade docstrings explicando qué se prueba
   - Usa nombres descriptivos
   - Agrupa tests relacionados en clases

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa esta guía de solución de problemas
2. Verifica que todas las dependencias están instaladas
3. Consulta los logs en `./logs/` (si están habilitados)
4. Abre un issue en GitHub con:
   - Descripción del problema
   - Comando ejecutado
   - Output completo del error
   - Versión de Python y sistema operativo

---

## ✨ Resumen

Para verificar que todo funciona correctamente:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar .env (opcional para Alpha Vantage)
cp .env.example .env
# Editar .env con tu API key

# 3. Ejecutar tests unitarios
python -m pytest tests/ -v

# 4. Ejecutar test comprehensivo
python examples/comprehensive_test.py

# 5. Verificar reportes generados
ls reports/
ls reports/plots/
```

Si todos los pasos se completan sin errores, ¡el toolkit está funcionando correctamente! 🎉
