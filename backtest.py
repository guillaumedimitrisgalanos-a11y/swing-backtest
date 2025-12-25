"""Backtesting engine for swing trading."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from config import Config
from metrics import compute_drawdown, summarize_results


@dataclass
class BacktestResult:
    equity: pd.DataFrame
    drawdown: pd.DataFrame
    trades: pd.DataFrame
    summary: dict


def run_backtest(data: pd.DataFrame, signals: pd.DataFrame, config: Config) -> BacktestResult:
    if "signal" not in signals:
        raise ValueError("Signals DataFrame must contain a 'signal' column.")

    data = data.copy().sort_index()
    signals = signals.reindex(data.index).fillna(0)

    cash = config.initial_capital
    position = 0  # number of shares held
    trade_profits: List[float] = []
    trades_records = []
    equity_curve = []

    costs = config.commission + config.slippage
    prev_entry_value = 0.0

    for i in range(1, len(data)):
        today = data.iloc[i]
        yesterday_signal = signals.iloc[i - 1]["signal"]

        # Enter long position
        if yesterday_signal == 1 and position == 0:
            trade_price = today["Open"] * (1 + costs)
            position = int(cash // trade_price)
            if position > 0:
                spend = position * trade_price
                cash -= spend
                prev_entry_value = spend
                trades_records.append(
                    {
                        "date": data.index[i].strftime("%Y-%m-%d"),
                        "action": "BUY",
                        "price": round(float(trade_price), 4),
                        "shares": position,
                        "cash_after": round(float(cash), 2),
                    }
                )

        # Exit to flat
        if yesterday_signal == 0 and position > 0:
            trade_price = today["Open"] * (1 - costs)
            proceeds = position * trade_price
            cash += proceeds
            profit = proceeds - prev_entry_value
            trade_profits.append(profit)
            trades_records.append(
                {
                    "date": data.index[i].strftime("%Y-%m-%d"),
                    "action": "SELL",
                    "price": round(float(trade_price), 4),
                    "shares": position,
                    "cash_after": round(float(cash), 2),
                }
            )
            position = 0
            prev_entry_value = 0.0

        equity = cash + position * today["Close"]
        equity_curve.append({"date": data.index[i], "equity": equity})

    equity_df = pd.DataFrame(equity_curve).set_index("date")
    drawdown_df = compute_drawdown(equity_df["equity"])
    trades_df = pd.DataFrame(trades_records)

    summary = summarize_results(
        equity=equity_df["equity"],
        drawdown=drawdown_df["drawdown"],
        trade_profits=trade_profits,
        trades_count=len(trades_records),
        config=config,
    )

    return BacktestResult(
        equity=equity_df,
        drawdown=drawdown_df,
        trades=trades_df,
        summary=summary,
    )
