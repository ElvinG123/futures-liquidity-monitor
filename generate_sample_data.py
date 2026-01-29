import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate(rows: int = 20000, out_csv: str = "sample_trades.csv") -> None:
    np.random.seed(42)

    start_time = datetime(2025, 1, 1, 9, 30)
    # Create increasing timestamps (trade-like arrivals)
    timestamps = [
        start_time + timedelta(seconds=int(x))
        for x in np.random.exponential(scale=20, size=rows).cumsum()
    ]

    instruments = np.random.choice(["ES", "NQ", "CL", "GC"], rows, p=[0.45, 0.30, 0.15, 0.10])

    # Different typical price levels by instrument
    base_price = {"ES": 4800, "NQ": 17000, "CL": 75, "GC": 2050}
    price = np.array([np.random.normal(base_price[i], base_price[i] * 0.006) for i in instruments])
    price = np.round(price, 2)

    size = np.random.randint(1, 80, rows)
    participant = np.random.choice(["ClientA", "ClientB", "ClientC", "HFT1", "HFT2"], rows)

    # Synthetic bid/ask around price (for spread metric)
    spread_bps = np.random.choice([0.5, 1, 2, 3, 5], rows, p=[0.20, 0.30, 0.25, 0.15, 0.10])  # bps-like
    # Spread dollars approx: price * (bps/10000)
    spread = price * (spread_bps / 10000.0)
    bid = np.round(price - spread / 2, 2)
    ask = np.round(price + spread / 2, 2)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "instrument": instruments,
        "price": price,
        "bid": bid,
        "ask": ask,
        "size": size,
        "participant": participant,
    })

    df.to_csv(out_csv, index=False)
    print(f" Created {out_csv} with {len(df):,} rows")

if __name__ == "__main__":
    generate()
