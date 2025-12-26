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
   python run.py --symbol MSFT --start 2021-01-01 --end 2023-01-01 --short 10 --long 40 --capital 15000
   ```

## Caching price data
- Price downloads are cached in `data_cache/` using the symbol, start date, end date, and interval in the filename.
- Control caching with `--use-cache` (default `on`):
  - `on`: use cache when available, otherwise download and save
  - `refresh`: always download and overwrite cache
  - `off`: always download without reading cache

Examples:
```bash
python run.py --symbol KO --start 2010-01-01 --end 2024-01-01 --use-cache on
python run.py --symbol KO --start 2010-01-01 --end 2024-01-01 --use-cache refresh
```

## What happens
- Data is downloaded from Yahoo Finance.
- Signals implement a **pullback-in-trend** approach on the **Close** column:
  - Define the prevailing trend with a long simple moving average (default 50 days) that must be rising and below price.
  - Wait for price to dip under the short moving average (default 20 days) and then reclaim it to signal a pullback recovery.
  - Stay long while the uptrend filter holds; exit when price slips under the long average.
- Orders triggered by a signal are placed at the **next day Open**.
- Per-side costs applied to every trade: 0.01% commission + 0.05% slippage.
- Position sizing: the backtest buys as many whole shares as possible with available cash and exits to cash when the signal turns flat.

## Outputs
Files are written to the `outputs/` folder by default:
- `equity.csv` – daily equity curve after trades.
- `drawdown.csv` – equity and running drawdown series.
- `trades.csv` – each buy/sell with executed price, shares, and cash balance.
- `summary.json` – key performance metrics (returns, Sharpe, drawdown, trade stats).

## Example: Pullback trend test on Coca-Cola (KO)

1. Install dependencies (Python 3.11):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the pullback strategy for Coca-Cola with default 20/50-day moving averages:
   ```bash
   python run.py --symbol KO --start 2023-01-01 --end 2024-01-01
   ```
3. Review the outputs in `outputs/` (equity, drawdown, trades, and summary files).

## Project files
- `config.py` – default configuration values.
- `data.py` – downloads price data with yfinance.
- `strategy.py` – pullback-in-trend signal generator.
- `backtest.py` – portfolio simulation with costs and next-day execution.
- `metrics.py` – drawdown and summary calculations.
- `run.py` – command-line entry point wiring everything together.

## Notes
- The engine is intentionally small and friendly for non-programmers; edit `config.py` or CLI flags to adjust settings.
- If Yahoo Finance is temporarily unavailable, rerun the script after a short delay.
