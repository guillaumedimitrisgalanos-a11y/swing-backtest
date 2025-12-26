"""Run the swing trading backtest."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import Config, config as default_config
from data import fetch_price_data
from strategy import generate_signals
from backtest import run_backtest
from metrics import save_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Swing trading backtest")
    parser.add_argument("--symbol", default=default_config.symbol, help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--start", default=default_config.start, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=default_config.end, help="End date YYYY-MM-DD")
    parser.add_argument("--short", type=int, default=default_config.short_window, help="Short moving average window")
    parser.add_argument("--long", type=int, default=default_config.long_window, help="Long moving average window")
    parser.add_argument(
        "--capital", type=float, default=default_config.initial_capital, help="Starting capital in USD"
    )
    parser.add_argument(
        "--use-cache",
        choices=["on", "refresh", "off"],
        default=default_config.use_cache,
        help=(
            "Price data caching: 'on' uses cache when available, 'refresh' overwrites cache, "
            "'off' always downloads without reading cache."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_config.output_dir),
        help="Directory to store output files (equity.csv, drawdown.csv, trades.csv, summary.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = Config(
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        initial_capital=args.capital,
        short_window=args.short,
        long_window=args.long,
        commission=default_config.commission,
        slippage=default_config.slippage,
        cache_dir=default_config.cache_dir,
        use_cache=args.use_cache,
        output_dir=Path(args.output_dir),
    )

    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading data for {config.symbol} from {config.start} to {config.end}...")
    data = fetch_price_data(config)

    print("Calculating signals on the closing price...")
    signals = generate_signals(data, config)

    print("Running backtest with trades at next day open (including commission and slippage)...")
    result = run_backtest(data, signals, config)

    equity_path = output_dir / "equity.csv"
    drawdown_path = output_dir / "drawdown.csv"
    trades_path = output_dir / "trades.csv"
    summary_path = output_dir / "summary.json"

    result.equity.to_csv(equity_path)
    result.drawdown.to_csv(drawdown_path)
    result.trades.to_csv(trades_path, index=False)
    save_summary(result.summary, summary_path)

    print("Backtest finished. Files saved to:")
    print(f"- {equity_path}")
    print(f"- {drawdown_path}")
    print(f"- {trades_path}")
    print(f"- {summary_path}")


if __name__ == "__main__":
    main()
