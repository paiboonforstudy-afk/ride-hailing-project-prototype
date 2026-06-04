"""
Driver and customer pool generation for the ride data generator.

Pre-generates fixed pools of reusable drivers and customers
before the main generation loop. This enables realistic per-entity
analytics such as driver utilization, customer retention,
repeat ride rate, and lifetime value.

Call build_driver_pool() and build_customer_pool() once per
generation session, then pass the pools into generate_ride_record().
"""

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from faker import Faker

fake = Faker("th_TH")


@dataclass(frozen=True)
class Driver:
    """
    A reusable driver entity sampled per ride.

    frozen=True ensures pool entries are immutable
    and cannot be accidentally modified during generation.
    """
    driver_id:      str
    driver_name:    str
    driver_phone:   str
    driver_license: str


@dataclass(frozen=True)
class Customer:
    """
    A reusable customer (booker) entity sampled per ride.

    frozen=True ensures pool entries are immutable
    and cannot be accidentally modified during generation.
    """
    booker_id:    str
    booker_name:  str
    booker_email: str
    booker_phone: str


def build_driver_pool(size: int) -> list[Driver]:
    """
    Pre-generates a fixed pool of reusable drivers.

    Call once per generation session before the main loop.
    For 100,000 rides with size=1000, each driver averages ~100 rides —
    sufficient for driver utilization and performance analytics.

    Args:
        size (int): Number of unique drivers to generate.

    Returns:
        list[Driver]: Fixed pool sampled randomly per ride.
    """
    pool = []
    for _ in range(size):
        pool.append(Driver(
            driver_id=      str(uuid.uuid4()),
            driver_name=    fake.name(),
            driver_phone=   fake.phone_number(),
            driver_license= fake.bothify("########"),
        ))
    return pool


def load_driver_pool(path: str | Path) -> list[Driver]:
    """
    Loads a pre-generated driver pool from a JSON file.

    Args:
        path (str | Path): Path to the driver_pool.json file.

    Returns:
        list[Driver]: Reconstructed driver pool.

    Raises:
        FileNotFoundError: If the file does not exist.
                           Run generate_pools.py first.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Driver pool file not found: {path}\n"
            "Run generate_pools.py first to build the pool."
        )
    with path.open("r", encoding="utf-8") as f:
        pool = []
        for d in json.load(f):
            pool.append(Driver(**d))
        return pool


def load_customer_pool(path: str | Path) -> list[Customer]:
    """
    Loads a pre-generated customer pool from a JSON file.

    Args:
        path (str | Path): Path to the customer_pool.json file.

    Returns:
        list[Customer]: Reconstructed customer pool.

    Raises:
        FileNotFoundError: If the file does not exist.
                           Run generate_pools.py first.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Customer pool file not found: {path}\n"
            "Run generate_pools.py first to build the pool."
        )
    with path.open("r", encoding="utf-8") as f:
        pool = []
        for c in json.load(f):
            pool.append(Customer(**c))
        return pool


def build_customer_pool(size: int) -> list[Customer]:
    """
    Pre-generates a fixed pool of reusable customers (bookers).

    Call once per generation session before the main loop.
    For 100,000 rides with size=10000, each customer averages ~10 rides —
    enabling repeat purchase rate, churn, and lifetime value analytics.

    Larger pool = more unique customers, lower repeat rate.
    Smaller pool = fewer unique customers, higher repeat rate.

    Args:
        size (int): Number of unique customers to generate.

    Returns:
        list[Customer]: Fixed pool sampled randomly per ride.
    """
    pool = []
    for _ in range(size):
        pool.append(Customer(
            booker_id=    str(uuid.uuid4()),
            booker_name=  fake.name(),
            booker_email= fake.email(),
            booker_phone= fake.phone_number(),
        ))
    return pool
