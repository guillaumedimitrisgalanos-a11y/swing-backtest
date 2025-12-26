"""Data loading utilities using yfinance."""

from __future__ import annotations

from pathlib import Path
from time import sleep

import pandas as pd
import yfinance as yf

from config import Config


def fetch_price_data(config: Config) -> pd.DataFrame:
    """
    Download OHLCV price data using yfinance.

    Parameters
    ----------
    config : Config
        Configuration with symbol and date range.

    Returns
    -------
    pd.DataFrame
        Price data indexed by date with OHLC columns.
    """

    config.cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = _cache_path(config)

    if config.use_cache == "on" and cache_path.exists():
        print(f"Loading cached data from {cache_path}")
        cached = _load_cache(cache_path)
        prepared_cached = _prepare_data(cached, config)
        if not prepared_cached.empty:
            return prepared_cached

    df = _download_with_retry(config)

    if df.empty:
        if cache_path.exists():
            print(f"Download failed, loading cached data from {cache_path}")
            df = _load_cache(cache_path)
        else:
            df = _load_local_fallback(config)
    else:
        df = _prepare_data(df, config)
        if config.use_cache in {"on", "refresh"}:
            _save_cache(df, cache_path)

    if not df.empty:
        df = _prepare_data(df, config)

    if df.empty:
        raise ValueError(
            "No data downloaded. Check symbol, date range, or provide a local fallback dataset."
        )

    return df


def _download_with_retry(config: Config) -> pd.DataFrame:
    """Attempt to download data with simple retry logic."""

    attempts = 3
    last_exception: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            df = yf.download(
                config.symbol,
                start=config.start,
                end=config.end,
                interval=config.interval,
                progress=False,
                auto_adjust=False,
                threads=False,
            )
            if not df.empty:
                return df
        except Exception as exc:  # pragma: no cover - defensive against network errors
            last_exception = exc

        # Small delay before retrying to avoid hammering the endpoint
        sleep(1 * attempt)

    if last_exception:
        print(f"Data download failed after {attempts} attempts: {last_exception}")
    return pd.DataFrame()


def _prepare_data(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Flatten columns, clean, and validate price data."""

    if isinstance(df.columns, pd.MultiIndex):
        if config.symbol in df.columns.get_level_values(-1):
            df = df.xs(config.symbol, level=-1, axis=1)
        else:
            df.columns = ["_".join(map(str, col)).strip("_") for col in df.columns]

    df = df.rename(columns=str.title)
    df = df.dropna()
    return df


def _cache_path(config: Config) -> Path:
    key = f"{config.symbol}_{config.start}_{config.end}_{config.interval}.csv"
    return config.cache_dir / key


def _load_cache(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["Date"], index_col="Date")


def _save_cache(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index_label="Date")


def _load_local_fallback(config: Config) -> pd.DataFrame:
    """Load data from a local CSV file when Yahoo Finance is unreachable."""

    candidate_paths: list[Path] = []

    if config.local_data_dir:
        base = Path(config.local_data_dir)
        candidate_paths.extend([
            base / f"{config.symbol}.csv",
            base / f"{config.symbol.lower()}.csv",
            base / f"{config.symbol.upper()}.csv",
        ])

    for path in candidate_paths:
        if path.exists():
            df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
            print(f"Loaded local data fallback from {path}")
            return df

    return pd.DataFrame()
