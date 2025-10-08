#!/usr/bin/env python3

import asyncio
import time
import random
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.infra.db import init_db, get_session
from app.domain.models import TransactionLedger

async def seed_transactions():
    """Seed the database with sample transaction data for testing"""
    await init_db()
    
    # Sample data
    customers = [f"cust_{i:04d}" for i in range(1, 101)]
    merchants = [
        "amzn_shop", "walmart_store", "target_retail", "netflix_sub", "spotify_music",
        "uber_rides", "starbucks_cafe", "mcdonalds_food", "gas_station_a", "grocery_mart",
        "fashion_store", "electronics_hub", "book_depot", "home_goods", "fitness_gym"
    ]
    
    transactions = []
    current_time = time.time()
    
    # Generate 500 sample transactions over the last 30 days
    for i in range(500):
        transaction = TransactionLedger(
            customer_id=random.choice(customers),
            merchant_id=random.choice(merchants),
            amount_cents=random.randint(500, 50000),  # $5 - $500
            currency=random.choice(["USD", "EUR", "GBP"]),
            occurred_at=current_time - random.randint(0, 30 * 24 * 3600),  # Last 30 days
            status=random.choice(["COMPLETED", "PENDING", "FAILED"]),
            transaction_type=random.choice(["PURCHASE", "REFUND", "AUTHORIZATION"])
        )
        transactions.append(transaction)
    
    # Insert into database
    async with get_session() as session:
        session.add_all(transactions)
        await session.commit()
    
    print(f"Seeded {len(transactions)} transactions")

if __name__ == "__main__":
    asyncio.run(seed_transactions())
