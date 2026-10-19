"""Quick debug script to test the pricing calculations - TODO: remove before release."""

from invoicer.models import LineItem
from invoicer.pricing import PriceCalculator

if __name__ == "__main__":
    print("🔍 Testing pricing calculations...")
    test_items = [LineItem(description="Test item", unit_price=10.0, quantity=2)]
    print(f"Subtotal: {PriceCalculator.calculate_order_subtotal(test_items)}")
    print("✅ Done!")
