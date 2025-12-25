"""Data loading utilities using yfinance."""

from __future__ import annotations

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

    df = yf.download(
        config.symbol,
        start=config.start,
        end=config.end,
        progress=False,
        auto_adjust=False,
    )

    df = df.rename(columns=str.title)
    df = df.dropna()

    if df.empty:
        raise ValueError("No data downloaded. Check symbol and date range.")

    return df
