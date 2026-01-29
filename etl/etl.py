import sqlite3
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


@dataclass
class ETLConfig:
    raw_csv: str = "sample_trades.csv"
    out_dir: str = "data"
    parquet_name: str = "clean_trades.parquet"
    sqlite_name: str = "trades.db"
    table_name: str = "trades"


def ensure_dirs(cfg: ETLConfig) -> Path:
    out_path = Path(cfg.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path


def read_and_clean(cfg: ETLConfig) -> pd.DataFrame:
    df = pd.read_csv(cfg.raw_csv, parse_dates=["timestamp"])

    df = df.dropna(subset=["timestamp", "instrument", "price", "size"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["bid"] = pd.to_numeric(df["bid"], errors="coerce")
    df["ask"] = pd.to_numeric(df["ask"], errors="coerce")
    df["size"] = pd.to_numeric(df["size"], errors="coerce")

    df = df.dropna(subset=["price", "bid", "ask", "size"])
    df = df[df["size"] > 0]
    df = df[df["ask"] >= df["bid"]]

    df["mid"] = (df["bid"] + df["ask"]) / 2.0
    df["spread"] = df["ask"] - df["bid"]
    df["notional"] = df["price"] * df["size"]

    df["ingested_at_utc"] = datetime.now(timezone.utc)
    df["trade_date"] = df["timestamp"].dt.date.astype(str)
    df["minute"] = df["timestamp"].dt.floor("min")

    return df


def write_parquet(df: pd.DataFrame, out_path: Path, cfg: ETLConfig) -> Path:
    parquet_path = out_path / cfg.parquet_name
    df.to_parquet(parquet_path, index=False)
    return parquet_path


def load_sqlite(df: pd.DataFrame, out_path: Path, cfg: ETLConfig) -> Path:
    db_path = out_path / cfg.sqlite_name
    conn = sqlite3.connect(db_path)
    df.to_sql(cfg.table_name, conn, if_exists="replace", index=False)
    conn.close()
    return db_path


def main():
    cfg = ETLConfig()
    out_path = ensure_dirs(cfg)

    if not Path(cfg.raw_csv).exists():
        raise FileNotFoundError("Missing sample_trades.csv. Run: python3 generate_sample_data.py")

    df = read_and_clean(cfg)
    write_parquet(df, out_path, cfg)
    load_sqlite(df, out_path, cfg)

    print("ETL complete:", len(df), "rows")


if __name__ == "__main__":
    main()
