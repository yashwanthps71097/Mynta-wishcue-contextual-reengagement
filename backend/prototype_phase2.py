import datetime
import uuid
import json

# =========================================================================
# Mock Database & Cache Setup (Simulating Redis & Postgres)
# =========================================================================
class MockDatabase:
    def __init__(self):
        # Maps userId -> list of wishlisted item dicts
        self.wishlist_db = {
            "usr_987654": [
                {"product_id": "prod_nike_123", "added_at": datetime.datetime.now() - datetime.timedelta(days=26), "size": "UK 8"},
                {"product_id": "prod_zara_456", "added_at": datetime.datetime.now() - datetime.timedelta(days=5), "size": "M"},
                {"product_id": "prod_hnm_789", "added_at": datetime.datetime.now() - datetime.timedelta(days=12), "size": "L"}
            ]
        }
        # Catalog product details
        self.catalog_db = {
            "prod_nike_123": {"name": "Nike Air Max", "price": 8999, "stock": { "UK 8": 0, "UK 9": 5 }},
            "prod_zara_456": {"name": "Zara Linen Shirt", "price": 2999, "stock": { "S": 10, "M": 2 }},
            "prod_hnm_789": {"name": "H&M Slim Fit Jeans", "price": 1999, "stock": { "L": 15 }}
        }

db = MockDatabase()

# =========================================================================
# Task 2.1: Signal Detection Engine (SDE) Core
# =========================================================================
class SignalDetectionEngine:
    def __init__(self, db):
        self.db = db

    def process_catalog_update(self, event):
        """
        Consumes updates from Kafka's 'catalog-updates' topic.
        Checks for price drops and stock replenish signals.
        """
        product_id = event["product_id"]
        update_type = event["update_type"] # "PRICE" or "STOCK"
        
        # Cross reference with active wishlists to see if any user has saved this product
        for user_id, wishlist in self.db.wishlist_db.items():
            wishlist_item = next((item for item in wishlist if item["product_id"] == product_id), None)
            
            if wishlist_item:
                user_size = wishlist_item["size"]
                if update_type == "PRICE":
                    self.price_monitor(user_id, product_id, event, wishlist_item)
                elif update_type == "STOCK":
                    self.inventory_monitor(user_id, product_id, event, user_size)

    def price_monitor(self, user_id, product_id, event, wishlist_item):
        """
        Price Monitor logic:
        Flags price drops on wishlisted items.
        """
        old_price = event["old_price"]
        new_price = event["new_price"]
        
        if new_price < old_price:
            price_drop_pct = ((old_price - new_price) / old_price) * 100
            
            # Mitigation from Edge Cases: Minimum 10% drop threshold
            if price_drop_pct >= 10.0:
                signal = {
                    "signal_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "product_id": product_id,
                    "trigger_type": "PRICE_DROP",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "metadata": {
                        "old_price": old_price,
                        "new_price": new_price,
                        "drop_percentage": round(price_drop_pct, 1),
                        "size": wishlist_item["size"]
                    }
                }
                print(f"[PRICE MONITOR] Found signal: {json.dumps(signal, indent=2)}")
                return signal
        return None

    def inventory_monitor(self, user_id, product_id, event, user_size):
        """
        Inventory Monitor logic:
        Flags "Back in Stock" or "Low Stock" signals for wishlisted items in user's size.
        """
        size_stock = event["stock"].get(user_size, 0)
        old_stock = event.get("old_stock", {}).get(user_size, 0)
        
        signal = None
        
        # Scenario A: Back in Stock
        if old_stock == 0 and size_stock > 0:
            signal_type = "BACK_IN_STOCK"
        # Scenario B: Low Stock Warning (e.g., <= 2 items left)
        elif size_stock <= 2 and size_stock > 0 and old_stock > size_stock:
            signal_type = "LOW_STOCK"
        else:
            return None

        signal = {
            "signal_id": str(uuid.uuid4()),
            "user_id": user_id,
            "product_id": product_id,
            "trigger_type": signal_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": {
                "size": user_size,
                "current_stock": size_stock
            }
        }
        print(f"[INVENTORY MONITOR] Found signal: {json.dumps(signal, indent=2)}")
        return signal

# =========================================================================
# Task 2.2: Temporal Trigger Service
# =========================================================================
class TemporalTriggerService:
    def __init__(self, db):
        self.db = db

    def scan_expiring_wishlists(self):
        """
        Simulates a daily cron job scanning for items wishlisted 25-28 days ago.
        """
        print("\n[CRON] Starting daily scan for expiring wishlist items (25-28 day momentum window)...")
        now = datetime.datetime.now()
        signals_triggered = []

        for user_id, wishlist in self.db.wishlist_db.items():
            for item in wishlist:
                days_saved = (now - item["added_at"]).days
                
                # Check for the 25-28 day window
                if 25 <= days_saved <= 28:
                    signal = {
                        "signal_id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "product_id": item["product_id"],
                        "trigger_type": "TEMPORAL_30D",
                        "timestamp": now.isoformat(),
                        "metadata": {
                            "days_saved": days_saved,
                            "days_remaining": 30 - days_saved
                        }
                    }
                    print(f"[TEMPORAL SERVICE] Found expiring item: {json.dumps(signal, indent=2)}")
                    signals_triggered.append(signal)
        return signals_triggered


# =========================================================================
# Demonstration Run
# =========================================================================
if __name__ == "__main__":
    sde = SignalDetectionEngine(db)
    temporal_service = TemporalTriggerService(db)

    print("--- 1. Simulating Catalog Price Update Event (Price Drop) ---")
    mock_price_event = {
        "product_id": "prod_zara_456",
        "update_type": "PRICE",
        "old_price": 2999,
        "new_price": 2499 # ~16.6% price drop
    }
    sde.process_catalog_update(mock_price_event)

    print("\n--- 2. Simulating Catalog Stock Update Event (Back In Stock) ---")
    mock_stock_event = {
        "product_id": "prod_nike_123",
        "update_type": "STOCK",
        "old_stock": {"UK 8": 0, "UK 9": 5},
        "stock": {"UK 8": 10, "UK 9": 3}
    }
    sde.process_catalog_update(mock_stock_event)

    print("\n--- 3. Simulating Temporal Trigger (Cron Scan) ---")
    temporal_service.scan_expiring_wishlists()
