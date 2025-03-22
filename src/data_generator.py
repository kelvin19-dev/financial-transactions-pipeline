# src/data_generator.py
import json
import csv
import os
import random
from datetime import datetime, timedelta
import uuid

def generate_transaction_data(num_records=100, output_dir="data", seed: int = None):
    """Generate sample financial transaction data in both CSV and JSON formats."""
    
    # Set seed if provided
    if seed is not None:
        random.seed(seed)
    
    os.makedirs(output_dir, exist_ok=True)
    
    transaction_types = ["PAYMENT", "DEPOSIT", "WITHDRAWAL", "TRANSFER", "REFUND"]
    statuses = ["COMPLETED", "PENDING", "FAILED", "CANCELLED"]
    
    records = []
    start_date = datetime.now() - timedelta(days=30)
    
    for _ in range(num_records):
        days_ago = random.randint(0, 29)
        transaction_date = start_date + timedelta(days=days_ago)
        date_str = transaction_date.strftime("%Y-%m-%d")
        
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "currency": "KES",
            "transaction_type": random.choice(transaction_types),
            "status": random.choice(statuses),
            "date": date_str,
            "customer": {
                "customer_id": f"CUST-{random.randint(1000, 9999)}",
                "name": f"Customer {random.randint(1, 100)}",
                "email": f"customer{random.randint(1, 100)}@example.com"
            },
            "metadata": {
                "ip_address": f"192.168.0.{random.randint(1, 255)}",
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "location": random.choice(["Nairobi", "Mombasa", "Kisumu", "Eldoret", "Nakuru"])
            }
        }
        records.append(transaction)
    
    # Append a timestamp to file names
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = os.path.join(output_dir, f"transactions_{timestamp}.csv")
    json_filename = os.path.join(output_dir, f"transactions_{timestamp}.json")
    
    # Write to CSV file
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ["transaction_id", "amount", "currency", "transaction_type", 
                      "status", "date", "customer_id", "customer_name", 
                      "customer_email", "ip_address", "device", "location"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in records:
            flat_record = {
                "transaction_id": record["transaction_id"],
                "amount": record["amount"],
                "currency": record["currency"],
                "transaction_type": record["transaction_type"],
                "status": record["status"],
                "date": record["date"],
                "customer_id": record["customer"]["customer_id"],
                "customer_name": record["customer"]["name"],
                "customer_email": record["customer"]["email"],
                "ip_address": record["metadata"]["ip_address"],
                "device": record["metadata"]["device"],
                "location": record["metadata"]["location"]
            }
            writer.writerow(flat_record)
    
    # Write to JSON file
    with open(json_filename, 'w') as jsonfile:
        json.dump(records, jsonfile, indent=2)
    
    print(f"Generated {num_records} records in CSV format: {csv_filename}")
    print(f"Generated {num_records} records in JSON format: {json_filename}")

if __name__ == "__main__":
    generate_transaction_data(num_records=500)
