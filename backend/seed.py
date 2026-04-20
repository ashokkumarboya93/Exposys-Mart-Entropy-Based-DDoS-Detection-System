"""
Database Seed Script
---------------------
Seeds the database with:
- Default admin user (bcrypt hashed)
- Default hacker user (bcrypt hashed)
- Sample store user
- Initial entropy baseline data
"""

from __future__ import annotations

import sys
import os

# Ensure app modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.db_models import (
    AdminUser, HackerUser, User,
    EntropyHistory, TrafficEvent, SessionLog, StoreProduct
)
from app.core.constants import PRODUCT_CATALOG


def seed():
    """Seed the database with initial data."""
    print("🌱 Initializing database...")
    init_db()

    db = SessionLocal()

    try:
        # ── Admin User ────────────────────────────────────────────
        existing_admin = db.query(AdminUser).filter(
            AdminUser.username == settings.ADMIN_USERNAME
        ).first()

        if not existing_admin:
            admin = AdminUser(
                username=settings.ADMIN_USERNAME,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
            db.add(admin)
            print(f"  ✅ Admin user created: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
        else:
            print(f"  ⏭️  Admin user already exists: {settings.ADMIN_USERNAME}")

        # ── Default Hacker User ───────────────────────────────────
        existing_hacker = db.query(HackerUser).filter(
            HackerUser.username == "darknet"
        ).first()

        if not existing_hacker:
            hacker = HackerUser(
                username="darknet",
                hashed_password=hash_password("ddos@2024"),
                alias="DARKNET",
            )
            db.add(hacker)
            print("  ✅ Hacker user created: darknet / ddos@2024")
        else:
            print("  ⏭️  Hacker user already exists: darknet")

        # ── Default Store User ────────────────────────────────────
        existing_user = db.query(User).filter(
            User.username == "shopper"
        ).first()

        if not existing_user:
            user = User(
                username="shopper",
                email="shopper@exposysmart.com",
                hashed_password=hash_password("shop123"),
                full_name="Test Shopper",
            )
            db.add(user)
            print("  ✅ Store user created: shopper / shop123")
        else:
            print("  ⏭️  Store user already exists: shopper")

        # ── Seed Entropy Baseline ─────────────────────────────────
        entropy_count = db.query(EntropyHistory).count()
        if entropy_count < 5:
            now = datetime.utcnow()
            for i in range(5):
                entry = EntropyHistory(
                    timestamp=now - timedelta(minutes=5 - i),
                    entropy_value=round(random.uniform(3.5, 4.5), 4),
                    normalized_entropy=round(random.uniform(0.75, 0.95), 4),
                    max_possible_entropy=round(random.uniform(4.0, 5.0), 4),
                    baseline_entropy=None,
                    threshold=None,
                    status="NORMAL",
                    total_requests=random.randint(50, 200),
                    unique_ips=random.randint(20, 50),
                )
                db.add(entry)
            print("  ✅ Seeded 5 entropy baseline records")
        else:
            print(f"  ⏭️  Entropy history already has {entropy_count} records")

        # ── Seed Normal Traffic ───────────────────────────────────
        traffic_count = db.query(TrafficEvent).count()
        if traffic_count < 10:
            pages = ["/store/homepage", "/store/product", "/store/cart", "/store/checkout"]
            actions = ["pageview", "click", "add_to_cart", "search"]
            now = datetime.utcnow()

            for i in range(20):
                event = TrafficEvent(
                    timestamp=now - timedelta(minutes=random.randint(1, 60)),
                    ip_address=f"192.168.1.{random.randint(1, 254)}",
                    endpoint=random.choice(pages),
                    method="GET",
                    traffic_type="normal",
                    session_id=f"seed-{i}",
                    action=random.choice(actions),
                    request_count=random.randint(1, 5),
                )
                db.add(event)
            print("  ✅ Seeded 20 normal traffic events")
        else:
            print(f"  ⏭️  Traffic events already has {traffic_count} records")

        # ── Seed Products ─────────────────────────────────────────
        product_count = db.query(StoreProduct).count()
        if product_count == 0:
            for p_data in PRODUCT_CATALOG:
                prod = StoreProduct(
                    id=p_data["id"],
                    name=p_data["name"],
                    brand=p_data["brand"],
                    price=p_data["price"],
                    original_price=p_data["original_price"],
                    image=p_data["image"],
                    category=p_data["category"],
                    rating=p_data["rating"],
                    reviews=p_data["reviews"],
                    badge=p_data["badge"],
                    description=p_data["description"],
                    specs=p_data["specs"]
                )
                db.add(prod)
            print(f"  ✅ Seeded {len(PRODUCT_CATALOG)} products")
        else:
            print(f"  ⏭️  Products already seeded ({product_count})")

        db.commit()
        print("\n🎉 Database seeding complete!")
        print("\n📋 Login Credentials:")
        print("  ┌──────────────┬──────────┬──────────┐")
        print("  │ Role         │ Username │ Password │")
        print("  ├──────────────┼──────────┼──────────┤")
        print("  │ Admin        │ admin    │ admin123 │")
        print("  │ Hacker       │ darknet  │ ddos@2024│")
        print("  │ Store User   │ shopper  │ shop123  │")
        print("  └──────────────┴──────────┴──────────┘")

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Seeding failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
