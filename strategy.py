"""Simple moving average crossover strategy."""

from __future__ import annotations

import pandas as pd

from config import Config


def generate_signals(data: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Create trading signals based on the close price.

    A long signal (1) is generated when the short moving average crosses above
    the long moving average. Otherwise the strategy stays flat (0).

    Parameters
    ----------
    data : pd.DataFrame
        Price data with a ``Close`` column.
    config : Config
        Strategy configuration.

    Returns
    -------
    pd.DataFrame
        DataFrame with ``signal`` and moving averages.
    """

    signals = pd.DataFrame(index=data.index)
    signals["short_ma"] = data["Close"].rolling(window=config.short_window).mean()
    signals["long_ma"] = data["Close"].rolling(window=config.long_window).mean()
    signals["signal"] = 0
    crossover = signals["short_ma"] > signals["long_ma"]
    signals.loc[crossover, "signal"] = 1
    signals = signals.fillna(0)
    return signals
