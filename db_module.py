import pymongo
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION

class PaymentDatabase:
    """
    Handles interactions with MongoDB for payment data retrieval
    """
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_COLLECTION]
        print(f"Connected to MongoDB: {MONGO_DB_NAME}.{MONGO_COLLECTION}")

    def get_payment_by_id(self, payment_id):
        """
        Retrieve payment information by payment ID
        
        Args:
            payment_id (str): The unique payment identifier
            
        Returns:
            dict: Payment information or None if not found
        """
        try:
            result = self.collection.find_one({"payment_id": payment_id})
            return result
        except Exception as e:
            print(f"Error retrieving payment {payment_id}: {e}")
            return None
    
    def close(self):
        """Close the MongoDB connection"""
        self.client.close()
        
    # Helper method to initialize the database with sample data (for testing)
    def initialize_sample_data(self):
        """Create sample payment data for testing purposes"""
        sample_payments = [
            {
                "payment_id": "PAY123456",
                "customer_name": "John Doe",
                "customer_email": "john.doe@example.com",
                "amount": 129.99,
                "currency": "USD",
                "status": "completed",
                "items": [
                    {"name": "Premium Headphones", "quantity": 1, "price": 129.99}
                ],
                "date": "2025-05-10T14:30:45"
            },
            {
                "payment_id": "PAY789012",
                "customer_name": "Jane Smith",
                "customer_email": "jane.smith@example.com",
                "amount": 75.50,
                "currency": "USD",
                "status": "processing",
                "items": [
                    {"name": "Wireless Mouse", "quantity": 1, "price": 45.50},
                    {"name": "USB-C Cable", "quantity": 2, "price": 15.00}
                ],
                "date": "2025-05-12T09:15:22"
            },
            {
                "payment_id": "PAY345678",
                "customer_name": "Alex Johnson",
                "customer_email": "alex.j@example.com",
                "amount": 199.95,
                "currency": "USD",
                "status": "completed",
                "items": [
                    {"name": "Smart Watch", "quantity": 1, "price": 199.95}
                ],
                "date": "2025-05-08T16:45:33"
            }
        ]
        
        # Delete existing sample data and insert new ones
        self.collection.delete_many({"payment_id": {"$in": [p["payment_id"] for p in sample_payments]}})
        self.collection.insert_many(sample_payments)
        print(f"Initialized {len(sample_payments)} sample payment records")

# Testing functionality
if __name__ == "__main__":
    db = PaymentDatabase()
    db.initialize_sample_data()
    
    # Test retrieval
    payment = db.get_payment_by_id("PAY123456")
    if payment:
        print(f"Found payment: {payment['payment_id']} - {payment['amount']} {payment['currency']}")
        print(f"Status: {payment['status']}")
        print("Items:")
        for item in payment['items']:
            print(f"  - {item['name']} (Qty: {item['quantity']}) - ${item['price']}")
    else:
        print("Payment not found")
    
    db.close()