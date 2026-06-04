"""
Pool pre-generation script.

Builds driver and customer pools based on RuntimeConfig defaults
and saves them to data/pools/ as JSON files for reuse across
multiple parallel historical generation runs.

Run this once before launching parallel terminals:

    python generate_pools.py

Then reference the saved pools in each terminal:

    python data_generator.py historical --count 25000 --format csv \
        --duration 2026-01-01:2026-02-01 \
        --driver-pool data/pools/driver_pool.json \
        --customer-pool data/pools/customer_pool.json
"""

import json
from dataclasses import asdict
from pathlib import Path

from generator.config import DEFAULT_CONFIG
from generator.pool import build_driver_pool, build_customer_pool


POOLS_DIR = Path("data/pools")


def run() -> None:
    config = DEFAULT_CONFIG

    POOLS_DIR.mkdir(parents=True, exist_ok=True)

    # --- Build pools ---
    print(f"Building driver pool   : {config.driver_pool_size:,} drivers...")
    driver_pool = build_driver_pool(config.driver_pool_size)

    print(f"Building customer pool : {config.customer_pool_size:,} customers...")
    customer_pool = build_customer_pool(config.customer_pool_size)

    # --- Save to files ---
    driver_path   = POOLS_DIR / f"driver_pool_{config.driver_pool_size}.json"
    customer_path = POOLS_DIR / f"customer_pool_{config.customer_pool_size}.json"

    with driver_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(d) for d in driver_pool], f, ensure_ascii=False, indent=2)

    with customer_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in customer_pool], f, ensure_ascii=False, indent=2)

    # --- Summary ---
    print()
    print("=" * 50)
    print("Pools saved successfully.")
    print("=" * 50)
    print(f"Driver pool   : {len(driver_pool):,} drivers   → {driver_path}")
    print(f"Customer pool : {len(customer_pool):,} customers → {customer_path}")


if __name__ == "__main__":
    run()
