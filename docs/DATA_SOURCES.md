# Fuentes de Datos

Este documento describe las fuentes de datos disponibles en el toolkit y cómo utilizarlas.

## 📊 Fuentes Disponibles

### 1. Yahoo Finance (Gratis)

**Extractor**: `YahooFinanceExtractor`

**Características**:
- ✅ **Gratis**: No requiere API key
- ✅ **Amplia cobertura**: Acciones, índices, ETFs, criptomonedas, forex
- ✅ **Datos históricos**: Hasta décadas de historia
- ✅ **Datos fundamentales**: P/E ratio, market cap, etc.
- ⚠️ **Limitaciones**: Rate limiting no documentado, puede ser inestable

**Tipos de activos soportados**:
- Acciones: `AAPL`, `MSFT`, `GOOGL`
- Índices: `^GSPC` (S&P 500), `^DJI` (Dow Jones), `^IXIC` (NASDAQ)
- Criptomonedas: `BTC-USD`, `ETH-USD`
- Forex: `EURUSD=X`, `GBPUSD=X`
- ETFs: `SPY`, `QQQ`, `VOO`

**Ejemplo de uso**:
```python
from src.extractors.yahoo_finance import YahooFinanceExtractor
from datetime import datetime, timedelta

extractor = YahooFinanceExtractor()

# Acción
apple = extractor.get_historical_prices("AAPL", start_date, end_date)

# Índice
sp500 = extractor.get_index_data("^GSPC", start_date, end_date)

# Criptomoneda
bitcoin = extractor.get_crypto_data("BTC-USD", start_date, end_date)

# Forex
eurusd = extractor.get_forex_data("EUR", "USD", start_date, end_date)

# Fundamentales
fundamentals = extractor.get_fundamentals("AAPL")
```

---

### 2. Alpha Vantage (API Key Requerida)

**Extractor**: `AlphaVantageExtractor`

**Características**:
- 🔑 **API Key requerida**: Gratis con límites (5 requests/min, 500/día)
- ✅ **Datos de alta calidad**: Datos ajustados y validados
- ✅ **Múltiples tipos**: Acciones, forex, criptomonedas, indicadores técnicos
- ✅ **Datos fundamentales**: Estados financieros, earnings
- ⚠️ **Limitaciones**: Rate limiting estricto en plan gratuito

**Obtener API Key**:
1. Visita: https://www.alphavantage.co/support/#api-key
2. Registra tu email
3. Copia tu API key
4. Añádela al archivo `.env`:
   ```
   ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
   ```

**Tipos de activos soportados**:
- Acciones: US y principales mercados internacionales
- Forex: Pares principales
- Criptomonedas: Bitcoin, Ethereum, etc.
- Indicadores técnicos: SMA, EMA, RSI, MACD

**Ejemplo de uso**:
```python
from src.extractors.alpha_vantage import AlphaVantageExtractor
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

extractor = AlphaVantageExtractor(api_key=api_key)

# Acción
apple = extractor.get_historical_prices("AAPL", start_date, end_date)

# Forex
eurusd = extractor.get_forex_data("EUR", "USD", start_date, end_date)

# Cripto
bitcoin = extractor.get_crypto_data("BTC", start_date, end_date)
```

---

### 3. Stooq (Gratis)

**Extractor**: `StooqExtractor`

**Características**:
- ✅ **Gratis**: No requiere API key
- ✅ **Bonos**: Excelente cobertura de bonos del tesoro
- ✅ **Mercados internacionales**: Acciones de múltiples países
- ✅ **Datos históricos**: Amplia historia disponible
- ⚠️ **Limitaciones**: Solo datos diarios, formato de símbolos específico

**Tipos de activos soportados**:
- Acciones US: `AAPL.US`, `MSFT.US`, `GOOGL.US`
- Índices: `^SPX` (S&P 500), `^DJI` (Dow Jones), `^NDQ` (NASDAQ)
- Bonos: `10USY.B` (10-year Treasury), `2USY.B`, `30USY.B`
- Criptomonedas: `BTC.USD`, `ETH.USD`
- Acciones internacionales: `AAPL.UK`, `BMW.DE`, `TOYOTA.JP`

**Formato de símbolos**:
- US stocks: Añadir `.US` (ej: `AAPL.US`)
- Índices: Usar `^` prefix (ej: `^SPX`)
- Bonos: Añadir `.B` (ej: `10USY.B`)
- Cripto: Añadir `.USD` (ej: `BTC.USD`)

**Ejemplo de uso**:
```python
from src.extractors.stooq import StooqExtractor

extractor = StooqExtractor()

# Acción US
apple = extractor.get_us_stock_data("AAPL", start_date, end_date)

# Índice
sp500 = extractor.get_index_data("^SPX", start_date, end_date)

# Bono
treasury_10y = extractor.get_bond_data("10USY.B", start_date, end_date)

# Criptomoneda
bitcoin = extractor.get_crypto_data("BTC", start_date, end_date)
```

---

## 🔄 Comparación de Fuentes

| Característica | Yahoo Finance | Alpha Vantage | Stooq |
|---------------|---------------|---------------|-------|
| **API Key** | No | Sí (gratis) | No |
| **Rate Limits** | No documentado | 5/min, 500/día | No documentado |
| **Acciones** | ✅ Excelente | ✅ Excelente | ✅ Bueno |
| **Índices** | ✅ Excelente | ⚠️ Limitado | ✅ Excelente |
| **Criptomonedas** | ✅ Excelente | ✅ Bueno | ✅ Bueno |
| **Bonos** | ⚠️ Limitado | ❌ No | ✅ Excelente |
| **Forex** | ✅ Bueno | ✅ Excelente | ⚠️ Limitado |
| **Fundamentales** | ✅ Sí | ✅ Sí | ❌ No |
| **Intervalos** | 1m, 5m, 1h, 1d, 1wk, 1mo | 1min, 5min, 15min, 30min, 60min, daily | Solo daily |
| **Historia** | Décadas | Años | Décadas |
| **Estabilidad** | ⚠️ Media | ✅ Alta | ✅ Alta |

---

## 🎯 Recomendaciones de Uso

### Para Acciones
1. **Primera opción**: Yahoo Finance (gratis, amplia cobertura)
2. **Alternativa**: Stooq (si Yahoo falla)
3. **Datos premium**: Alpha Vantage (mejor calidad)

### Para Índices
1. **Primera opción**: Yahoo Finance o Stooq
2. **Alternativa**: Alpha Vantage (cobertura limitada)

### Para Criptomonedas
1. **Primera opción**: Yahoo Finance (más actualizado)
2. **Alternativa**: Stooq o Alpha Vantage

### Para Bonos
1. **Primera opción**: Stooq (mejor cobertura)
2. **Alternativa**: Yahoo Finance (limitado)

### Para Forex
1. **Primera opción**: Alpha Vantage (mejor calidad)
2. **Alternativa**: Yahoo Finance

### Para Datos Fundamentales
- **Única opción**: Yahoo Finance o Alpha Vantage

---

## 🔧 Configuración

### Archivo .env

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui

# Polygon API Key (futuro)
POLYGON_API_KEY=tu_api_key_aqui

# Configuración
DEFAULT_CACHE_DIR=./cache
LOG_LEVEL=INFO
```

### Ejemplo .env.example

Ya existe un archivo `.env.example` que puedes copiar:

```bash
cp .env.example .env
# Edita .env con tus API keys
```

---

## 🚀 Uso Avanzado

### Descarga Concurrente de Múltiples Fuentes

```python
from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.extractors.stooq import StooqExtractor
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Crear extractores
yahoo = YahooFinanceExtractor()
stooq = StooqExtractor()

# Descargar el mismo activo de ambas fuentes
aapl_yahoo = yahoo.get_historical_prices("AAPL", start_date, end_date)
aapl_stooq = stooq.get_us_stock_data("AAPL", start_date, end_date)

# Comparar datos
print(f"Yahoo: {len(aapl_yahoo)} records")
print(f"Stooq: {len(aapl_stooq)} records")

# Verificar correlación
correlation = aapl_yahoo.data.set_index('date')['close'].corr(
    aapl_stooq.data.set_index('date')['close']
)
print(f"Correlation: {correlation:.4f}")
```

### Fallback entre Fuentes

```python
def get_data_with_fallback(symbol, start_date, end_date):
    """Intenta descargar de múltiples fuentes con fallback."""
    
    # Intentar Yahoo Finance primero
    try:
        yahoo = YahooFinanceExtractor()
        return yahoo.get_historical_prices(symbol, start_date, end_date)
    except Exception as e:
        print(f"Yahoo failed: {e}")
    
    # Intentar Stooq
    try:
        stooq = StooqExtractor()
        return stooq.get_us_stock_data(symbol, start_date, end_date)
    except Exception as e:
        print(f"Stooq failed: {e}")
    
    # Intentar Alpha Vantage
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        alpha = AlphaVantageExtractor(api_key=os.getenv('ALPHA_VANTAGE_API_KEY'))
        return alpha.get_historical_prices(symbol, start_date, end_date)
    except Exception as e:
        print(f"Alpha Vantage failed: {e}")
    
    raise Exception(f"Could not download {symbol} from any source")
```

---

## 📚 Recursos Adicionales

### Yahoo Finance
- Documentación: https://pypi.org/project/yfinance/
- Símbolos: https://finance.yahoo.com/

### Alpha Vantage
- Website: https://www.alphavantage.co/
- Documentación: https://www.alphavantage.co/documentation/
- API Key: https://www.alphavantage.co/support/#api-key

### Stooq
- Website: https://stooq.com/
- Símbolos: https://stooq.com/db/l/
- Documentación pandas-datareader: https://pandas-datareader.readthedocs.io/

---

## ⚠️ Consideraciones Importantes

1. **Rate Limiting**: Respeta los límites de cada API
2. **Caching**: Considera implementar cache para evitar descargas repetidas
3. **Error Handling**: Siempre maneja excepciones al descargar datos
4. **Validación**: Valida los datos después de descargarlos
5. **Backup**: Ten múltiples fuentes como backup
6. **Costos**: Verifica los costos de planes premium si necesitas más requests
7. **Términos de Servicio**: Lee y respeta los términos de cada proveedor

---

## 🔮 Futuras Fuentes

Fuentes planeadas para futuras versiones:

- **Polygon.io**: Datos en tiempo real y históricos
- **IEX Cloud**: Datos de mercado y fundamentales
- **Quandl**: Datos económicos y alternativos
- **FRED**: Datos económicos de la Reserva Federal
- **Binance**: Datos de criptomonedas
- **CoinGecko**: Datos de criptomonedas

---

Para más información sobre cómo usar los extractores, consulta los ejemplos en la carpeta `examples/`.
