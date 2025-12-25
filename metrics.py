"""Performance metrics helpers."""

from __future__ import annotations

import json
from typing import Dict, List

import numpy as np
import pandas as pd

from config import Config


def compute_drawdown(equity: pd.Series) -> pd.DataFrame:
    cumulative_high = equity.cummax()
    drawdown = (equity - cumulative_high) / cumulative_high
    return pd.DataFrame({"equity": equity, "drawdown": drawdown})


def summarize_results(
    equity: pd.Series,
    drawdown: pd.Series,
    trade_profits: List[float],
    trades_count: int,
    config: Config,
) -> Dict[str, float]:
    returns = equity.pct_change().dropna()
    total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
    annual_return = (1 + total_return) ** (252 / len(equity)) - 1 if len(equity) > 1 else 0
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (returns.mean() * 252) / volatility if volatility != 0 else 0
    max_drawdown = drawdown.min()
    win_rate = 0
    if trade_profits:
        wins = sum(1 for p in trade_profits if p > 0)
        win_rate = wins / len(trade_profits)

    summary = {
        "symbol": config.symbol,
        "start": config.start,
        "end": config.end,
        "total_return": round(total_return, 4),
        "annual_return": round(annual_return, 4),
        "volatility": round(float(volatility), 4),
        "sharpe_ratio": round(float(sharpe_ratio), 4),
        "max_drawdown": round(float(max_drawdown), 4),
        "trades": trades_count,
        "completed_trades": len(trade_profits),
        "win_rate": round(float(win_rate), 4),
        "initial_capital": config.initial_capital,
        "ending_equity": round(float(equity.iloc[-1]), 2),
    }
    return summary


def save_summary(summary: Dict[str, float], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
