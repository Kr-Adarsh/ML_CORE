orders = {
    "ORD-101": {
        "status": "shipped",
        "tracking_id": "TRK-101",
        "items": [{"name": "Wireless Mouse", "quantity": 1, "price": 29.99}],
        "total_price": 29.99
    },
    "ORD-102": {
        "status": "delivered",
        "tracking_id": "TRK-102",
        "items": [
            {"name": "Mechanical Keyboard", "quantity": 1, "price": 89.99},
            {"name": "Desk Mat", "quantity": 2, "price": 15.00}
        ],
        "total_price": 119.99
    },
    "ORD-103": {
        "status": "processing",
        "tracking_id": None,
        "items": [{"name": "27-inch Monitor", "quantity": 1, "price": 249.99}],
        "total_price": 249.99
    },
    "ORD-104": {
        "status": "cancelled",
        "tracking_id": None,
        "items": [{"name": "USB-C Hub", "quantity": 1, "price": 34.50}],
        "total_price": 34.50
    },
    "ORD-105": {
        "status": "returned",
        "tracking_id": "TRK-105",
        "items": [{"name": "Noise Cancelling Headphones", "quantity": 1, "price": 199.99}],
        "total_price": 199.99
    }
}

tracking = {
    "TRK-101": {
        "status": "in_transit",
        "estimated_delivery": "2026-10-30",
        "carrier": "FedEx",
        "current_location": "Memphis Hub, TN"
    },
    "TRK-102": {
        "status": "delivered",
        "estimated_delivery": "2026-10-25",
        "carrier": "UPS",
        "current_location": "Front Door / Porch"
    },
    "TRK-105": {
        "status": "out_for_delivery",
        "estimated_delivery": "2026-10-27",
        "carrier": "DHL",
        "current_location": "Local Delivery Facility"
    },
    "TRK-202": {
        "status": "exception",
        "estimated_delivery": "Pending",
        "carrier": "USPS",
        "current_location": "Weather Delay - Chicago Network Distribution Center"
    }
}



# def lookup_order(order_id: str):
def lookup_order(order_id: str):
    return orders.get(order_id, {"error": "Order not found"})

def lookup_tracking(tracking_id : str):
    return tracking.get(tracking_id, {"error": "Tracking not found"})



tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Get shipping details for an order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order identifier"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    }
]