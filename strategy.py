"""Pullback-in-trend signal generator."""

from __future__ import annotations

import pandas as pd

from config import Config


def generate_signals(data: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Create pullback-in-trend trading signals on the close price.

    The approach stays in cash until an uptrend is established, then enters
    after a shallow pullback toward the short moving average. The position is
    held while the uptrend persists and exits when price closes back under the
    long-term average.

    Parameters
    ----------
    data : pd.DataFrame
        Price data with a ``Close`` column.
    config : Config
        Strategy configuration. ``short_window`` is used for the pullback
        anchor; ``long_window`` defines the prevailing trend filter.

    Returns
    -------
    pd.DataFrame
        DataFrame with ``signal``, moving averages, and helper columns that
        describe the trend and pullback recovery states.
    """

    signals = pd.DataFrame(index=data.index)
    signals["short_ma"] = data["Close"].rolling(window=config.short_window).mean()
    signals["long_ma"] = data["Close"].rolling(window=config.long_window).mean()

    long_ma_rising = signals["long_ma"] > signals["long_ma"].shift(1)
    price_above_long = data["Close"] > signals["long_ma"]
    trend_up = (long_ma_rising & price_above_long).fillna(False)

    pulled_back_yesterday = data["Close"].shift(1) < signals["short_ma"].shift(1)
    reclaimed_short_ma = data["Close"] >= signals["short_ma"]
    pullback_recovery = (pulled_back_yesterday & reclaimed_short_ma).fillna(False)

    signals["trend_up"] = trend_up
    signals["pullback_recovery"] = pullback_recovery

    # Build a stateful long/flat series: enter on a pullback recovery during an
    # uptrend, and stay long while the trend filter holds.
    signal_values = []
    in_position = False
    for i in range(len(signals)):
        if i == 0:
            signal_values.append(0)
            continue

        if not in_position and trend_up.iat[i] and pullback_recovery.iat[i]:
            in_position = True
        elif in_position:
            # Exit when the uptrend filter fails or price falls under the
            # long-term average.
            if (not trend_up.iat[i]) or data["Close"].iat[i] < signals["long_ma"].iat[i]:
                in_position = False

        signal_values.append(1 if in_position else 0)

    signals["signal"] = signal_values
    signals = signals.fillna(0)
    return signals
