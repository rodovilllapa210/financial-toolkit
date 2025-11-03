"""
Stooq data extractor (Versión B – Pro / Inteligente).

Características:
- Sin pandas_datareader: descarga directa del CSV oficial de Stooq.
- Normalización inteligente de símbolos (stocks, índices, crypto, bonos).
- Manejo robusto de CSV sin volumen y/o sin OHLC (imputación + metadata).
- Detección automática de bond YIELD vs PRICE y guardado en metadata.
- Crypto: mapeo BTC→BTCUSD, ETH→ETHUSD, etc. (si procede).
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from loguru import logger

from src.extractors.base import BaseExtractor
from src.models.price_series import PriceSeries

# --------------------------------------------------------------------------------------
# Constantes y normalización
# --------------------------------------------------------------------------------------

_STOOQ_BASE = "https://stooq.com/q/d/l/?s={symbol}&i=d"

_COMPLETE_PATTERNS = [
    re.compile(r".+\.B$", re.IGNORECASE),          # bonos/yields: ... .B
    re.compile(r"^[A-Z]{3,}USD$", re.IGNORECASE),  # BTCUSD, ETHUSD, etc.
    re.compile(r"^\^?[A-Z0-9._-]+$"),              # índices/tickers ya válidos
]

_CRYPTO_MAP_TO_USD = {"BTC", "ETH", "LTC", "XRP", "BCH"}

# Yield vs Price (heurística de Stooq para US Treasuries)
#   - Rendimiento: 10YUSY.B, 2YUSY.B, 30YUSY.B...
#   - Precio:      10YUSP.B, 30YUSP.B...
_YIELD_REGEX = re.compile(r"(^|\D)(\d+YUSY)\.B$", re.IGNORECASE)
_PRICE_REGEX = re.compile(r"(^|\D)(\d+YUSP)\.B$", re.IGNORECASE)


def _is_complete_symbol(sym: str) -> bool:
    return any(p.match(sym) for p in _COMPLETE_PATTERNS)


def _normalize_symbol(sym: str, kind: str) -> str:
    """
    Normaliza el símbolo para Stooq en función del tipo de activo:
    kind ∈ {"stock","index","crypto","bond"}.

    Reglas:
      - Si ya es “completo”, no tocar.
      - crypto: NO añadir '.USD' nunca. Espera BTCUSD/ETHUSD...
                Si te pasan 'BTC' / 'ETH' / 'LTC' / 'XRP' / 'BCH' => convertir a XXXUSD.
      - bond: si no tiene punto, añadir '.B' (Stooq).
      - stock/index: respetar lo que venga (añadimos .US o ^ en métodos específicos).
    """
    s = sym.strip().upper()
    if _is_complete_symbol(s):
        return s

    if kind == "crypto":
        if s.endswith("USD"):
            return s
        if s in _CRYPTO_MAP_TO_USD:
            return s + "USD"
        return s

    if kind == "bond":
        if "." not in s:
            return s + ".B"
        return s

    return s


def _fetch_stooq_csv(symbol: str) -> pd.DataFrame:
    """Descarga y normaliza el CSV de Stooq para un símbolo dado."""
    url = _STOOQ_BASE.format(symbol=symbol.lower())
    logger.debug(f"Fetching CSV from Stooq: {url}")
    df = pd.read_csv(url)

    if df is None or df.empty:
        raise ValueError(f"No data returned for {symbol}")

    # Normaliza nombres y columnas
    df.columns = [c.strip().lower() for c in df.columns]
    rename_map = {
        "date": "date", "open": "open", "high": "high",
        "low": "low", "close": "close", "vol": "volume", "volume": "volume"
    }
    df = df.rename(columns=rename_map)

    if "date" not in df.columns:
        raise ValueError(f"Stooq CSV for {symbol} has no 'date' column")

    # Si solo viene 'close', imputamos OHLC con close
    ohlc_cols = {"open", "high", "low"}
    if "close" in df.columns and not ohlc_cols.issubset(df.columns):
        close = df["close"]
        if "open" not in df.columns:
            df["open"] = close
        if "high" not in df.columns:
            df["high"] = close
        if "low" not in df.columns:
            df["low"] = close
        df.attrs["ohlc_imputed"] = True
    else:
        df.attrs["ohlc_imputed"] = False

    # 'volume' puede no existir: créala con 0
    if "volume" not in df.columns:
        df["volume"] = 0
        df.attrs["volume_missing"] = True
    else:
        df.attrs["volume_missing"] = False

    # Parseo de fecha y orden
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)
    if len(df) == 0:
        raise ValueError(f"No data returned for {symbol}")

    return df


def _detect_bond_type(symbol: str) -> str:
    """Devuelve 'yield' o 'price' para bonos US Treasuries según el símbolo."""
    s = symbol.upper()
    if _YIELD_REGEX.search(s):
        return "yield"
    if _PRICE_REGEX.search(s):
        return "price"
    # Heurística adicional: si contiene 'USY' => yield (2USY.B, 10YUSY.B...)
    if "USY" in s:
        return "yield"
    if "USP" in s:
        return "price"
    return "unknown"


def _determine_asset_type(symbol: str) -> str:
    s = symbol.upper()
    if s.startswith("^"):
        return "index"
    if s.endswith(".B") or "USY" in s or "USP" in s:
        return "bond"
    if s.endswith(".US") or "." in s and s.split(".")[-1].isalpha() and len(s.split(".")[-1]) <= 3:
        return "stock"
    if s.endswith("USD") or any(ccy in s for ccy in ["BTC", "ETH", "LTC", "XRP", "BCH"]):
        return "crypto"
    return "unknown"


def _get_name_from_symbol(symbol: str) -> str:
    mapping = {
        "^SPX": "S&P 500 Index",
        "^DJI": "Dow Jones Industrial Average",
        "^NDQ": "NASDAQ Composite",
        "10YUSY.B": "US 10Y Treasury Yield",
        "30YUSY.B": "US 30Y Treasury Yield",
        "2YUSY.B":  "US 2Y Treasury Yield",
        "10YUSP.B": "US 10Y Treasury Price",
        "30YUSP.B": "US 30Y Treasury Price",
        "BTCUSD":   "Bitcoin",
        "ETHUSD":   "Ethereum",
    }
    return mapping.get(symbol.upper(), symbol)


def _get_currency_from_symbol(symbol: str) -> str:
    s = symbol.upper()
    if any(tag in s for tag in [".USD", ".US", ".B"]) or s.startswith("^"):
        return "USD"
    if ".UK" in s:
        return "GBP"
    if any(tag in s for tag in [".DE", ".FR", ".ES", ".IT"]):
        return "EUR"
    if ".JP" in s:
        return "JPY"
    if s.endswith("USD"):
        return "USD"
    return "USD"


def _get_exchange_from_symbol(symbol: str) -> str:
    s = symbol.upper()
    if ".US" in s:
        return "US"
    if ".UK" in s:
        return "LSE"
    if ".DE" in s:
        return "XETRA"
    if ".JP" in s:
        return "TSE"
    if s.startswith("^"):
        return "INDEX"
    if s.endswith(".B"):
        return "BOND"
    if s.endswith("USD"):
        return "CRYPTO"
    return "Unknown"


# --------------------------------------------------------------------------------------
# Clase principal
# --------------------------------------------------------------------------------------

class StooqExtractor(BaseExtractor):
    """
    Extractor para datos de Stooq.

    Métodos:
      - get_historical_prices
      - get_index_data
      - get_crypto_data
      - get_bond_data
      - get_us_stock_data
      - search_symbol (placeholder)
    """

    def __init__(self, max_workers: int = 5):
        super().__init__(api_key=None, max_workers=max_workers)

    def _to_price_series(
        self,
        df: pd.DataFrame,
        symbol: str,
        name: str,
        source: str,
        asset_type: str,
        currency: str,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> PriceSeries:
        df = df.copy()

        # Asegura adjusted_close
        if "adjusted_close" not in df.columns:
            df["adjusted_close"] = df["close"]

        # Metadata básica + flags de imputación
        metadata: Dict[str, Any] = {
            "interval": "1d",
            "exchange": _get_exchange_from_symbol(symbol),
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        # Flags del fetcher
        metadata["ohlc_imputed"] = bool(df.attrs.get("ohlc_imputed", False))
        metadata["volume_missing"] = bool(df.attrs.get("volume_missing", False))

        return PriceSeries(
            symbol=symbol,
            name=name,
            data=df[["date", "open", "high", "low", "close", "volume", "adjusted_close"]],
            source=source,
            asset_type=asset_type,
            currency=currency,
            metadata=metadata,
        )

    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
        kind: Optional[str] = None,  # puede forzar normalización específica
    ) -> PriceSeries:
        """Descarga histórica desde Stooq para un símbolo ya normalizado o a normalizar."""
        try:
            sym = _normalize_symbol(symbol, kind or "stock")
            logger.debug(f"[Stooq] Fetching symbol={symbol} -> normalized={sym}, kind={kind or 'stock'}")

            df = _fetch_stooq_csv(sym)
            # Filtro por fechas
            msk = (df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))
            df = df.loc[msk].reset_index(drop=True)
            if df.empty:
                raise ValueError(f"No data returned in date range for {sym}")

            asset_type = _determine_asset_type(sym)
            name = _get_name_from_symbol(sym)
            currency = _get_currency_from_symbol(sym)

            extra: Dict[str, Any] = {}
            if asset_type == "bond":
                bond_type = _detect_bond_type(sym)
                extra["bond_type"] = bond_type

            ps = self._to_price_series(
                df=df,
                symbol=sym,
                name=name,
                source="stooq",
                asset_type=asset_type,
                currency=currency,
                extra_metadata=extra,
            )
            logger.debug(f"[Stooq] OK: {sym} -> {len(ps)} rows, asset_type={asset_type}")
            return ps

        except Exception as e:
            logger.error(f"Error fetching {symbol} from Stooq: {e}")
            raise

    # ----------------- Helpers públicos específicos -----------------

    def get_index_data(self, index_symbol: str, start_date: datetime, end_date: datetime) -> PriceSeries:
        sym = index_symbol if index_symbol.startswith("^") else f"^{index_symbol}"
        return self.get_historical_prices(sym, start_date, end_date, kind="index")

    def get_crypto_data(self, crypto_symbol: str, start_date: datetime, end_date: datetime) -> PriceSeries:
        # Normalización criptos: BTC -> BTCUSD; si ya viene BTCUSD lo respeta.
        sym = _normalize_symbol(crypto_symbol, kind="crypto")
        return self.get_historical_prices(sym, start_date, end_date, kind="crypto")

    def get_bond_data(self, bond_symbol: str, start_date: datetime, end_date: datetime) -> PriceSeries:
        # Normalización bonos: si falta sufijo .B y no hay punto, lo añade.
        sym = _normalize_symbol(bond_symbol, kind="bond")
        return self.get_historical_prices(sym, start_date, end_date, kind="bond")

    def get_us_stock_data(self, symbol: str, start_date: datetime, end_date: datetime) -> PriceSeries:
        sym = symbol.upper()
        if not sym.endswith(".US"):
            sym = f"{sym}.US"
        return self.get_historical_prices(sym, start_date, end_date, kind="stock")

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        logger.warning("Stooq doesn't support symbol search API. Returning query as-is.")
        return [{
            "symbol": query.upper(),
            "name": query.upper(),
            "type": "Unknown",
            "exchange": "Stooq",
        }]
