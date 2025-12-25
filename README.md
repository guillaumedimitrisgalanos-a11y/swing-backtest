# Swing Trading Backtest (Python 3.11)

A simple swing trading backtester that downloads market data with **yfinance**, builds signals on the **close** price, and executes trades at the **next day open**. Trading costs assume **0.01% commission** and **0.05% slippage** on every buy and sell.

## Quick start

1. Install dependencies (Python 3.11):
   ```bash
   pip install -r requirements.txt
   ```
2. Run a backtest (defaults: AAPL, 2022 calendar year, $10k starting capital):
   ```bash
   python run.py
   ```
3. Customize the run:
   ```bash
   python run.py --symbol MSFT --start 2021-01-01 --end 2023-01-01 --short 5 --long 20 --capital 15000
   ```

## What happens
- Data is downloaded from Yahoo Finance.
- Signals use a short/long simple moving average crossover on the **Close** column.
- Orders triggered by a signal are placed at the **next day Open**.
- Per-side costs applied to every trade: 0.01% commission + 0.05% slippage.
- Position sizing: the backtest buys as many whole shares as possible with available cash and exits to cash when the signal turns flat.

## Outputs
Files are written to the `outputs/` folder by default:
- `equity.csv` – daily equity curve after trades.
- `drawdown.csv` – equity and running drawdown series.
- `trades.csv` – each buy/sell with executed price, shares, and cash balance.
- `summary.json` – key performance metrics (returns, Sharpe, drawdown, trade stats).

## Project files
- `config.py` – default configuration values.
- `data.py` – downloads price data with yfinance.
- `strategy.py` – moving-average crossover signal generator.
- `backtest.py` – portfolio simulation with costs and next-day execution.
- `metrics.py` – drawdown and summary calculations.
- `run.py` – command-line entry point wiring everything together.

## Notes
- The engine is intentionally small and friendly for non-programmers; edit `config.py` or CLI flags to adjust settings.
- If Yahoo Finance is temporarily unavailable, rerun the script after a short delay.
