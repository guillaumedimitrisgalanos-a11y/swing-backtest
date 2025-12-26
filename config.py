from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Config:
    symbol: str = "AAPL"
    start: str = "2022-01-01"
    end: str = "2023-01-01"
    interval: str = "1d"
    initial_capital: float = 10000.0
    short_window: int = 20
    long_window: int = 50
    commission: float = 0.0001  # 0.01% per side
    slippage: float = 0.0005   # 0.05% per side
    data_source: str = "yahoo"
    output_dir: Path = Path("outputs")
    local_data_dir: Path | None = Path("sample_data")
    cache_dir: Path = Path("data_cache")
    use_cache: Literal["on", "refresh", "off"] = "on"


config = Config()
